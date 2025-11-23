import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var sessionViewModel: SessionViewModel

    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                if let user = sessionViewModel.currentUser {
                    VStack(spacing: 16) {
                        if let avatarUrl = user.avatarUrl, let url = URL(string: avatarUrl) {
                            AsyncImage(url: url) { image in
                                image
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                            } placeholder: {
                                Circle()
                                    .fill(Color.gray.opacity(0.3))
                            }
                            .frame(width: 100, height: 100)
                            .clipShape(Circle())
                        } else {
                            Circle()
                                .fill(Color.blue.opacity(0.3))
                                .frame(width: 100, height: 100)
                                .overlay {
                                    Text(user.name.prefix(1))
                                        .font(.system(size: 40))
                                        .foregroundColor(.blue)
                                }
                        }

                        Text(user.name)
                            .font(.title2)
                            .fontWeight(.bold)

                        if let bio = user.bio {
                            Text(bio)
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal)
                        }
                    }

                    Spacer()

                    Button {
                        sessionViewModel.setCurrentUser(nil)
                    } label: {
                        Text("Switch User")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                    }
                    .padding(.horizontal)
                }
            }
            .padding(.top, 32)
            .navigationTitle("Profile")
        }
    }
}
