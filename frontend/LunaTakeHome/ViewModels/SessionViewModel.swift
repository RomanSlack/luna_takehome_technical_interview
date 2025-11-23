import Foundation

@MainActor
class SessionViewModel: ObservableObject {
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var error: String?

    private let apiClient: APIClient

    init(apiClient: APIClient = .shared) {
        self.apiClient = apiClient
    }

    func setCurrentUser(_ user: User) {
        currentUser = user
    }

    func loadCurrentUser(userId: Int) async {
        isLoading = true
        error = nil

        do {
            let user = try await apiClient.getUser(id: userId)
            currentUser = user
        } catch {
            self.error = error.localizedDescription
        }

        isLoading = false
    }
}
