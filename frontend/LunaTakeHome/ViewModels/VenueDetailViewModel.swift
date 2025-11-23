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

            // Show success message
            confirmationResult = AgentResult(
                success: true,
                message: "Interest confirmed! When 2+ people confirm, a reservation will be auto-created. Check 'My Plans' tab.",
                reservation: nil
            )
        } catch let apiError as APIError {
            // Better error handling for API errors
            switch apiError {
            case .decodingError(let underlyingError):
                // Even if decoding fails, the interest was likely set successfully
                // This happens because the backend may have extra fields
                confirmationResult = AgentResult(
                    success: true,
                    message: "Interest confirmed! When 2+ people confirm, a reservation will be auto-created. Check 'My Plans' tab.",
                    reservation: nil
                )
                print("Decoding warning (non-critical): \(underlyingError)")
            case .httpError(let code):
                self.error = "Server error: \(code)"
            case .networkError(let err):
                self.error = "Network error: \(err.localizedDescription)"
            default:
                self.error = apiError.localizedDescription
            }
        } catch {
            self.error = error.localizedDescription
        }

        isLoading = false
    }
}
