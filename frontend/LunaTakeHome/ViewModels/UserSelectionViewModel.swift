import Foundation

@MainActor
class UserSelectionViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var error: String?

    private let apiClient: APIClient

    init(apiClient: APIClient = .shared) {
        self.apiClient = apiClient
    }

    func loadUsers() async {
        isLoading = true
        error = nil

        do {
            users = try await apiClient.fetchUsers()
        } catch {
            self.error = error.localizedDescription
        }

        isLoading = false
    }
}
