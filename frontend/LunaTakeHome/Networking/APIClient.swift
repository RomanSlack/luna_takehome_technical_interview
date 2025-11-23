import Foundation
import CoreLocation

enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(Int)
    case decodingError(Error)
    case networkError(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid response from server"
        case .httpError(let code):
            return "HTTP error: \(code)"
        case .decodingError(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        }
    }
}

class APIClient {
    static let shared = APIClient()

    private let baseURL: String
    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder

    init(baseURL: String = Config.apiBaseURL) {
        self.baseURL = baseURL
        self.session = URLSession.shared

        self.decoder = JSONDecoder()
        // Use custom date decoding to handle ISO8601 with fractional seconds
        let dateFormatter = ISO8601DateFormatter()
        dateFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        self.decoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let dateString = try container.decode(String.self)

            // Try with fractional seconds first
            if let date = dateFormatter.date(from: dateString) {
                return date
            }

            // Fallback to standard ISO8601
            dateFormatter.formatOptions = [.withInternetDateTime]
            if let date = dateFormatter.date(from: dateString) {
                return date
            }

            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Cannot decode date string \(dateString)")
        }

        self.encoder = JSONEncoder()
        self.encoder.dateEncodingStrategy = .iso8601
    }

    // MARK: - User Endpoints

    func fetchUsers() async throws -> [User] {
        let url = try buildURL(path: "/users")
        return try await performRequest(url: url, method: "GET")
    }

    func getUser(id: Int) async throws -> User {
        let url = try buildURL(path: "/users/\(id)")
        return try await performRequest(url: url, method: "GET")
    }

    func createUser(_ user: UserCreate) async throws -> User {
        let url = try buildURL(path: "/users")
        return try await performRequest(url: url, method: "POST", body: user)
    }

    // MARK: - Venue Endpoints

    func fetchVenues(category: String? = nil) async throws -> [Venue] {
        var queryItems: [URLQueryItem] = []
        if let category = category {
            queryItems.append(URLQueryItem(name: "category", value: category))
        }
        let url = try buildURL(path: "/venues", queryItems: queryItems)
        return try await performRequest(url: url, method: "GET")
    }

    func getVenue(id: Int) async throws -> Venue {
        let url = try buildURL(path: "/venues/\(id)")
        return try await performRequest(url: url, method: "GET")
    }

    // MARK: - Interest Endpoints

    func fetchInterests(userId: Int) async throws -> [UserInterest] {
        let url = try buildURL(path: "/users/\(userId)/interests")
        return try await performRequest(url: url, method: "GET")
    }

    func setInterest(userId: Int, interest: UserInterestCreate) async throws -> UserInterest {
        let url = try buildURL(path: "/users/\(userId)/interests")
        return try await performRequest(url: url, method: "POST", body: interest)
    }

    // MARK: - Recommendation Endpoints

    func fetchRecommendations(userId: Int, location: CLLocationCoordinate2D? = nil) async throws -> RecommendationsResponse {
        var queryItems: [URLQueryItem] = []
        if let location = location {
            queryItems.append(URLQueryItem(name: "lat", value: String(location.latitude)))
            queryItems.append(URLQueryItem(name: "lon", value: String(location.longitude)))
        }
        let url = try buildURL(path: "/recommendations/\(userId)", queryItems: queryItems)
        return try await performRequest(url: url, method: "GET")
    }

    // MARK: - Reservation Endpoints

    func fetchReservations(userId: Int) async throws -> [Reservation] {
        let url = try buildURL(path: "/reservations/\(userId)")
        return try await performRequest(url: url, method: "GET")
    }

    func createReservation(_ reservation: ReservationCreate) async throws -> Reservation {
        let url = try buildURL(path: "/reservations")
        return try await performRequest(url: url, method: "POST", body: reservation)
    }

    func acceptReservation(reservationId: Int, userId: Int) async throws -> AgentResult {
        let url = try buildURL(path: "/reservations/accept")
        let body = ReservationAccept(reservationId: reservationId, userId: userId)
        return try await performRequest(url: url, method: "POST", body: body)
    }

    // MARK: - Private Helper Methods

    private func buildURL(path: String, queryItems: [URLQueryItem] = []) throws -> URL {
        guard var components = URLComponents(string: baseURL + path) else {
            throw APIError.invalidURL
        }

        if !queryItems.isEmpty {
            components.queryItems = queryItems
        }

        guard let url = components.url else {
            throw APIError.invalidURL
        }

        return url
    }

    private func performRequest<T: Decodable>(
        url: URL,
        method: String,
        body: (some Encodable)? = Optional<String>.none
    ) async throws -> T {
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let body = body {
            request.httpBody = try encoder.encode(body)
        }

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(httpResponse.statusCode)
        }

        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingError(error)
        }
    }
}
