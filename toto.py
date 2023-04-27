import SwiftUI
import Combine

struct Movie: Identifiable, Codable {
    let id: Int
    let title: String
    let poster_path: String
    let overview: String
    
    var posterURL: URL {
        return URL(string: "https://image.tmdb.org/t/p/w500\(poster_path)")!
    }
}

struct MovieResponse: Codable {
    let results: [Movie]
}

class MovieAPI: ObservableObject {
    @Published var movies: [Movie] = []
    private var cancellable: AnyCancellable?
    private let userDefaults = UserDefaults.standard
    private var initialLoad = true
    
    init() {
        loadMoviesFromUserDefaults()
    }
    
    func initialFetch() {
        guard initialLoad else { return }
        initialLoad = false
        fetchMovies()
    }
    
    // get it here https://www.themoviedb.org/settings/api
    let apiKey = ""
    
    func fetchMovies() {
        guard movies.isEmpty else { return }
        let today = Date()
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let todayString = formatter.string(from: today)
        
        let randomPage = Int.random(in: 1...10)
        let url = URL(string: "https://api.themoviedb.org/3/discover/movie?api_key=\(apiKey)&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=\(randomPage)&primary_release_date.lte=\(todayString)&vote_count.gte=1000")!
        
        cancellable = URLSession.shared.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: MovieResponse.self, decoder: JSONDecoder())
            .replaceError(with: MovieResponse(results: []))
            .receive(on: DispatchQueue.main)
            .map { movies in
                let shuffledMovies = movies.results.shuffled()
                return Array(shuffledMovies.prefix(5))
            }
            .sink(receiveCompletion: { _ in }, receiveValue: { movies in
                self.movies = movies
                self.saveMoviesToUserDefaults()
            })
        
    }
    
    func fetchTrailerURL(for movie: Movie, completion: @escaping (String?) -> Void) {
        
        let urlString = "https://api.themoviedb.org/3/movie/\(movie.id)/videos?api_key=\(apiKey)&language=en-US"
        
        guard let url = URL(string: urlString) else {
            completion(nil)
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, _, _ in
            if let data = data,
               let jsonObject = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let results = jsonObject["results"] as? [[String: Any]],
               let firstVideo = results.first,
               let key = firstVideo["key"] as? String {
                completion("https://www.youtube.com/watch?v=\(key)")
            } else {
                completion(nil)
            }
        }.resume()
    }
    
    func fetchWatchProviders(for movie: Movie, completion: @escaping ([WatchProvider]?) -> Void) {
        let urlString = "https://api.themoviedb.org/3/movie/\(movie.id)/watch/providers?api_key=\(apiKey)"
        print("WP:", urlString)
        guard let url = URL(string: urlString) else {
            completion(nil)
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, _, _ in
            if let data = data {
                let decoder = JSONDecoder()
                do {
                    let watchProvidersResponse = try decoder.decode(WatchProvidersResponse.self, from: data)
                    completion(watchProvidersResponse.results.US?.flatrate)
                } catch {
                    print("Error decoding watch providers: \(error)")
                    completion(nil)
                }
            } else {
                completion(nil)
            }
        }.resume()
    }
    
    private func saveMoviesToUserDefaults() {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let todayString = formatter.string(from: Date())
        
        if let encodedMovies = try? JSONEncoder().encode(movies) {
            userDefaults.set(encodedMovies, forKey: "movies")
            userDefaults.set(todayString, forKey: "fetchDate")
            print("Movies saved to UserDefaults with date: \(todayString)", movies.map { $0.title }.joined())
        }
    }
    
    private func loadMoviesFromUserDefaults() {
        if let savedMovies = userDefaults.data(forKey: "movies"),
           let savedMoviesDate = userDefaults.string(forKey: "fetchDate") {
            let formatter = DateFormatter()
            formatter.dateFormat = "yyyy-MM-dd"
            let todayString = formatter.string(from: Date())
            
            print("Saved movies date: \(savedMoviesDate), Today's date: \(todayString)")
            
            if savedMoviesDate == todayString {
                if let decodedMovies = try? JSONDecoder().decode([Movie].self, from: savedMovies) {
                    movies = decodedMovies
                    print("Movies loaded from UserDefaults", movies.map { $0.title }.joined())
                }
            } else {
                print("Fetching new movies")
                fetchMovies()
            }
        } else {
            print("No saved movies found, fetching new movies")
            fetchMovies()
        }
    }
    
}

struct MovieCard: View {
    let movie: Movie
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                AsyncImage(url: movie.posterURL) { image in
                    image.resizable()
                } placeholder: {
                    ProgressView()
                }
                .aspectRatio(contentMode: .fill)
                .frame(width: geometry.size.width, height: geometry.size.height)
                .clipped()
            }
        }
        .edgesIgnoringSafeArea(.all)
    }
}

struct ContentView: View {
    @StateObject private var movieAPI = MovieAPI()
    @State private var currentPage = 0
    
    @State private var selectedMovie: Movie?
    
    var body: some View {
        ZStack {
            Color.black
                .edgesIgnoringSafeArea(.all)
            
            TabView(selection: $currentPage) {
                ForEach(movieAPI.movies) { movie in
                    MovieCard(movie: movie)
                        .onTapGesture {
                            print("Setting selected", movie.title)
                            selectedMovie = movie
                        }
                }
            }
            .sheet(item: $selectedMovie) { movie in
                MovieDetailsView(movie: movie)
                
            }
            
            .tabViewStyle(PageTabViewStyle())
            .onAppear {
                movieAPI.initialFetch()
            }
            
            VStack {
                Spacer()
                Text("\(currentPage + 1)/\(movieAPI.movies.count)")
                
                    .padding(.bottom, 10)
            }
            .foregroundColor(.white)
        }.background(.black)
    }
}

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}


struct MovieDetailsView: View {
    let movie: Movie
    @State private var trailerURL: URL?
    @StateObject private var movieAPI = MovieAPI()
    @State private var watchProviders: [WatchProvider] = []
    
    var body: some View {
        ScrollView {
            
            VStack(alignment: .leading, spacing: 10) {
                
                if let url = trailerURL {
                    WebView(request: URLRequest(url: url))
                        .frame(height: UIScreen.main.bounds.width * 9 / 16)
                        .transition(.opacity.animation(.easeIn(duration: 0.4).delay(1)))
                } else {
                    ProgressView()
                        .frame(height: UIScreen.main.bounds.width * 9 / 16)
                }
                
                Text(movie.title)
                    .font(.largeTitle)
                    .foregroundColor(.white)
                    .fontWeight(.bold)
                    .foregroundColor(.black)
                
                Text(movie.overview)
                    .font(.body)
                    .foregroundColor(.white)
                    .lineLimit(nil)
                    .truncationMode(.tail)
                
                
                if !watchProviders.isEmpty {
                    Text("Available On")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .padding(.top)
                    
                    HStack {
                        ForEach(watchProviders) { provider in
                            
                            AsyncImage(url: URL(string: "https://image.tmdb.org/t/p/original\(provider.logoPath)")) { image in
                                image.resizable()
                            } placeholder: {
                                RoundedRectangle(cornerRadius: 5)
                                    .fill(Color.gray)
                                    .frame(width: 50, height: 50)
                            }
                            .frame(width: 50, height: 50)
                            .clipShape(RoundedRectangle(cornerRadius: 5))
                            
                            
                        }
                    }
                }
                
                
                Spacer()
            }
            .padding(20)
            .onAppear {
                movieAPI.fetchTrailerURL(for: movie) { urlString in
                    if let urlString = urlString {
                        DispatchQueue.main.async {
                            trailerURL = URL(string: urlString)
                        }
                    }
                }
                
                
                movieAPI.fetchWatchProviders(for: movie) { providers in
                    if let providers = providers {
                        print("got providers", providers.map { $0.logoPath }.joined())
                        DispatchQueue.main.async {
                            watchProviders = providers
                        }
                    }
                }
                
            }.background(Color.black.edgesIgnoringSafeArea(.all))
        }.background(.black)
    }
}


import WebKit
struct WebView: UIViewRepresentable {
    let request: URLRequest
    
    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.allowsBackForwardNavigationGestures = true
        return webView
    }
    
    func updateUIView(_ uiView: WKWebView, context: Context) {
        uiView.load(request)
    }
}


struct WatchProvidersResponse: Codable {
    let results: WatchProvidersResults
}

struct WatchProvidersResults: Codable {
    let US: WatchProviders?
    
    enum CodingKeys: String, CodingKey {
        case US = "US"
    }
}

struct WatchProviders: Codable {
    let flatrate: [WatchProvider]?
}

struct WatchProvider: Codable, Identifiable {
    let id = UUID()
    let logoPath: String
    let name: String

    enum CodingKeys: String, CodingKey {
        case id
        case logoPath = "logo_path"
        case name = "provider_name"
    }
}
