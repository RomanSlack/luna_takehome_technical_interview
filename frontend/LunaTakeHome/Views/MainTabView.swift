import SwiftUI

struct MainTabView: View {
    @EnvironmentObject var sessionViewModel: SessionViewModel

    var body: some View {
        TabView {
            RecommendationsView()
                .tabItem {
                    Label("Discover", systemImage: "sparkles")
                }

            MyReservationsView()
                .tabItem {
                    Label("My Plans", systemImage: "calendar")
                }

            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.circle")
                }
        }
    }
}
