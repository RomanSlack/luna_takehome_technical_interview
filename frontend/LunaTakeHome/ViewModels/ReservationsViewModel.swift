import Foundation

@MainActor
class ReservationsViewModel: ObservableObject {
    @Published var reservations: [Reservation] = []
    @Published var isLoading = false
    @Published var error: String?

    private let apiClient: APIClient

    init(apiClient: APIClient = .shared) {
        self.apiClient = apiClient
    }

    func loadReservations(userId: Int) async {
        isLoading = true
        error = nil

        do {
            reservations = try await apiClient.fetchReservations(userId: userId)
        } catch {
            self.error = error.localizedDescription
        }

        isLoading = false
    }

    func acceptReservation(reservationId: Int, userId: Int) async {
        do {
            let result = try await apiClient.acceptReservation(reservationId: reservationId, userId: userId)

            if result.success {
                // Refresh reservations
                await loadReservations(userId: userId)
            } else {
                error = result.message
            }
        } catch {
            self.error = error.localizedDescription
        }
    }

    func refresh(userId: Int) async {
        await loadReservations(userId: userId)
    }
}
