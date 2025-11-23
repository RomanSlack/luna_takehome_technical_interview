import Foundation

@MainActor
class VenueDetailViewModel: ObservableObject {
    @Published var venue: Venue
    @Published var recommendedPeople: [RecommendedPerson]
    @Published var isLoading = false
    @Published var error: String?
    @Published var confirmationResult: AgentResult?

    private let apiClient: APIClient

    init(venue: Venue, recommendedPeople: [RecommendedPerson], apiClient: APIClient = .shared) {
        self.venue = venue
        self.recommendedPeople = recommendedPeople
        self.apiClient = apiClient
    }

    func confirmGoing(userId: Int) async {
        isLoading = true
        error = nil
        confirmationResult = nil

        do {
            // Set interest to CONFIRMED
            let interest = UserInterestCreate(venueId: venue.id, status: .confirmed)
            _ = try await apiClient.setInterest(userId: userId, interest: interest)

            // For now, just show success
            // In a full implementation, this would trigger the agent to create a reservation
            // when all parties have confirmed
            confirmationResult = AgentResult(
                success: true,
                message: "Interest confirmed! You'll be notified when others confirm.",
                reservation: nil
            )
        } catch {
            self.error = error.localizedDescription
        }

        isLoading = false
    }
}
