import SwiftUI

struct VenueDetailView: View {
    @EnvironmentObject var sessionViewModel: SessionViewModel
    @StateObject private var viewModel: VenueDetailViewModel

    init(venue: Venue, recommendedPeople: [RecommendedPerson]) {
        _viewModel = StateObject(wrappedValue: VenueDetailViewModel(
            venue: venue,
            recommendedPeople: recommendedPeople
        ))
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(viewModel.venue.name)
                        .font(.title)
                        .fontWeight(.bold)

                    Text(viewModel.venue.category.capitalized)
                        .font(.subheadline)
                        .foregroundColor(.secondary)

                    HStack {
                        Image(systemName: "location.fill")
                            .foregroundColor(.secondary)
                        Text(viewModel.venue.address)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.horizontal)

                if let description = viewModel.venue.description {
                    Divider()

                    VStack(alignment: .leading, spacing: 8) {
                        Text("About")
                            .font(.headline)
                        Text(description)
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                    .padding(.horizontal)
                }

                if !viewModel.recommendedPeople.isEmpty {
                    Divider()

                    VStack(alignment: .leading, spacing: 12) {
                        Text("Recommended People")
                            .font(.headline)
                            .padding(.horizontal)

                        ForEach(viewModel.recommendedPeople) { person in
                            HStack {
                                if let avatarUrl = person.user.avatarUrl, let url = URL(string: avatarUrl) {
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
                                }

                                VStack(alignment: .leading, spacing: 4) {
                                    Text(person.user.name)
                                        .font(.headline)

                                    if let bio = person.user.bio {
                                        Text(bio)
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                            .lineLimit(1)
                                    }
                                }
                                .padding(.leading, 8)

                                Spacer()

                                Text("\(Int(person.compatibilityScore))%")
                                    .font(.caption)
                                    .foregroundColor(.blue)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(Color.blue.opacity(0.1))
                                    .cornerRadius(8)
                            }
                            .padding(.horizontal)
                        }
                    }
                }

                if let error = viewModel.error {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                        .padding(.horizontal)
                }

                if let result = viewModel.confirmationResult {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Image(systemName: result.success ? "checkmark.circle.fill" : "exclamationmark.circle.fill")
                                .foregroundColor(result.success ? .green : .red)
                            Text(result.message)
                                .font(.subheadline)
                        }
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
                    .padding(.horizontal)
                }

                Button {
                    Task {
                        if let userId = sessionViewModel.currentUser?.id {
                            await viewModel.confirmGoing(userId: userId)
                        }
                    }
                } label: {
                    HStack {
                        if viewModel.isLoading {
                            ProgressView()
                                .tint(.white)
                        } else {
                            Image(systemName: "checkmark.circle.fill")
                            Text("Confirm Going")
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
                }
                .disabled(viewModel.isLoading)
                .padding(.horizontal)
                .padding(.bottom)
            }
            .padding(.vertical)
        }
        .navigationBarTitleDisplayMode(.inline)
    }
}
