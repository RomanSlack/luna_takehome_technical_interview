import SwiftUI

struct UserSelectionView: View {
    @EnvironmentObject var sessionViewModel: SessionViewModel
    @StateObject private var viewModel = UserSelectionViewModel()

    var body: some View {
        NavigationView {
            VStack {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.error {
                    VStack(spacing: 16) {
                        Text("Error loading users")
                            .font(.headline)
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Button("Retry") {
                            Task {
                                await viewModel.loadUsers()
                            }
                        }
                    }
                    .padding()
                } else if viewModel.users.isEmpty {
                    VStack(spacing: 16) {
                        Text("No users available")
                            .font(.headline)
                        Text("Make sure the backend is running and seeded with data")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                        Button("Reload") {
                            Task {
                                await viewModel.loadUsers()
                            }
                        }
                    }
                    .padding()
                } else {
                    List(viewModel.users) { user in
                        Button {
                            sessionViewModel.setCurrentUser(user)
                        } label: {
                            HStack {
                                if let avatarUrl = user.avatarUrl, let url = URL(string: avatarUrl) {
                                    AsyncImage(url: url) { image in
                                        image
                                            .resizable()
                                            .aspectRatio(contentMode: .fill)
                                    } placeholder: {
                                        Circle()
                                            .fill(Color.gray.opacity(0.3))
                                    }
                                    .frame(width: 50, height: 50)
                                    .clipShape(Circle())
                                } else {
                                    Circle()
                                        .fill(Color.blue.opacity(0.3))
                                        .frame(width: 50, height: 50)
                                        .overlay {
                                            Text(user.name.prefix(1))
                                                .font(.title2)
                                                .foregroundColor(.blue)
                                        }
                                }

                                VStack(alignment: .leading, spacing: 4) {
                                    Text(user.name)
                                        .font(.headline)

                                    if let bio = user.bio {
                                        Text(bio)
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                            .lineLimit(1)
                                    }
                                }
                                .padding(.leading, 8)

                                Spacer()

                                Image(systemName: "chevron.right")
                                    .foregroundColor(.secondary)
                            }
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .navigationTitle("Select User")
            .task {
                await viewModel.loadUsers()
            }
        }
    }
}
