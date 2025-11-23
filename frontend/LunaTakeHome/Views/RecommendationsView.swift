import SwiftUI
import CoreLocation

struct RecommendationsView: View {
    @EnvironmentObject var sessionViewModel: SessionViewModel
    @StateObject private var viewModel = RecommendationsViewModel()

    var body: some View {
        NavigationView {
            VStack {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.error {
                    VStack(spacing: 16) {
                        Text("Error loading recommendations")
                            .font(.headline)
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                } else if viewModel.recommendations.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "sparkles")
                            .font(.system(size: 60))
                            .foregroundColor(.secondary)
                        Text("No recommendations yet")
                            .font(.headline)
                        Text("Check back soon for personalized venue suggestions")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                } else {
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            ForEach(viewModel.recommendations) { recommendation in
                                NavigationLink(destination: VenueDetailView(
                                    venue: recommendation.venue,
                                    recommendedPeople: recommendation.recommendedPeople
                                )) {
                                    VenueRecommendationCard(recommendation: recommendation)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                        .padding()
                    }
                    .refreshable {
                        if let userId = sessionViewModel.currentUser?.id {
                            await viewModel.refresh(userId: userId)
                        }
                    }
                }
            }
            .navigationTitle("Discover")
            .task {
                if let userId = sessionViewModel.currentUser?.id {
                    // Using NYC Times Square as default location for recommendations
                    let nycLocation = CLLocationCoordinate2D(latitude: 40.7589, longitude: -73.9851)
                    await viewModel.loadRecommendations(userId: userId, location: nycLocation)
                }
            }
        }
    }
}

struct VenueRecommendationCard: View {
    let recommendation: RecommendedVenue

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(recommendation.venue.name)
                        .font(.headline)

                    Text(recommendation.venue.category.capitalized)
                        .font(.caption)
                        .foregroundColor(.secondary)

                    Text(recommendation.venue.address)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }

                Spacer()

                VStack(alignment: .trailing) {
                    Text("Score: \(Int(recommendation.score))")
                        .font(.caption)
                        .foregroundColor(.blue)
                }
            }

            if !recommendation.recommendedPeople.isEmpty {
                Divider()

                VStack(alignment: .leading, spacing: 8) {
                    Text("Friends interested")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    HStack(spacing: -8) {
                        ForEach(recommendation.recommendedPeople.prefix(5)) { person in
                            if let avatarUrl = person.user.avatarUrl, let url = URL(string: avatarUrl) {
                                AsyncImage(url: url) { image in
                                    image
                                        .resizable()
                                        .aspectRatio(contentMode: .fill)
                                } placeholder: {
                                    Circle()
                                        .fill(Color.gray.opacity(0.3))
                                }
                                .frame(width: 32, height: 32)
                                .clipShape(Circle())
                                .overlay(
                                    Circle()
                                        .stroke(Color.white, lineWidth: 2)
                                )
                            } else {
                                Circle()
                                    .fill(Color.blue.opacity(0.3))
                                    .frame(width: 32, height: 32)
                                    .overlay(
                                        Circle()
                                            .stroke(Color.white, lineWidth: 2)
                                    )
                            }
                        }

                        if recommendation.recommendedPeople.count > 5 {
                            Text("+\(recommendation.recommendedPeople.count - 5)")
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .padding(.leading, 8)
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
    }
}
