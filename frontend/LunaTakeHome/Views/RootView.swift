import SwiftUI

struct RootView: View {
    @EnvironmentObject var sessionViewModel: SessionViewModel

    var body: some View {
        Group {
            if sessionViewModel.currentUser != nil {
                MainTabView()
            } else {
                UserSelectionView()
            }
        }
    }
}
