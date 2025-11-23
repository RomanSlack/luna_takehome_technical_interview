import Foundation
import CoreLocation

@MainActor
class RecommendationsViewModel: ObservableObject {
    @Published var recommendations: [RecommendedVenue] = []
    @Published var isLoading = false
    @Published var error: String?

    private let apiClient: APIClient
    private var userId: Int?

    init(apiClient: APIClient = .shared) {
        self.apiClient = apiClient
    }

    func loadRecommendations(userId: Int, location: CLLocationCoordinate2D? = nil) async {
        self.userId = userId
        isLoading = true
        error = nil

        do {
            let response = try await apiClient.fetchRecommendations(userId: userId, location: location)
            recommendations = response.recommendedVenues
        } catch {
            self.error = error.localizedDescription
        }

        isLoading = false
    }

    func refresh(userId: Int, location: CLLocationCoordinate2D? = nil) async {
        await loadRecommendations(userId: userId, location: location)
    }

    func setInterest(userId: Int, venueId: Int, status: InterestStatus) async {
        do {
            let interest = UserInterestCreate(venueId: venueId, status: status)
            _ = try await apiClient.setInterest(userId: userId, interest: interest)

            // Refresh recommendations after setting interest
            await loadRecommendations(userId: userId)
        } catch {
            self.error = error.localizedDescription
        }
    }
}
