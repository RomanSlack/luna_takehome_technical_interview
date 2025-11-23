import SwiftUI

struct MyReservationsView: View {
    @EnvironmentObject var sessionViewModel: SessionViewModel
    @StateObject private var viewModel = ReservationsViewModel()

    var body: some View {
        NavigationView {
            VStack {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.error {
                    VStack(spacing: 16) {
                        Text("Error loading reservations")
                            .font(.headline)
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                } else if viewModel.reservations.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "calendar")
                            .font(.system(size: 60))
                            .foregroundColor(.secondary)
                        Text("No plans yet")
                            .font(.headline)
                        Text("Confirm your interest in venues to create plans with friends")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                } else {
                    List {
                        ForEach(viewModel.reservations) { reservation in
                            NavigationLink(destination: ReservationDetailView(
                                reservation: reservation,
                                onAccept: {
                                    if let userId = sessionViewModel.currentUser?.id {
                                        await viewModel.acceptReservation(
                                            reservationId: reservation.id,
                                            userId: userId
                                        )
                                    }
                                }
                            )) {
                                ReservationRow(reservation: reservation)
                            }
                        }
                    }
                    .refreshable {
                        if let userId = sessionViewModel.currentUser?.id {
                            await viewModel.refresh(userId: userId)
                        }
                    }
                }
            }
            .navigationTitle("My Plans")
            .task {
                if let userId = sessionViewModel.currentUser?.id {
                    await viewModel.loadReservations(userId: userId)
                }
            }
            .onAppear {
                // Refresh reservations when tab appears
                Task {
                    if let userId = sessionViewModel.currentUser?.id {
                        await viewModel.loadReservations(userId: userId)
                    }
                }
            }
        }
    }
}

struct ReservationRow: View {
    let reservation: Reservation

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(reservation.venue.name)
                    .font(.headline)

                Spacer()

                Text(reservation.status.rawValue.capitalized)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(statusColor.opacity(0.2))
                    .foregroundColor(statusColor)
                    .cornerRadius(8)
            }

            Text(reservation.time, style: .date)
                .font(.subheadline)
                .foregroundColor(.secondary)

            Text(reservation.time, style: .time)
                .font(.caption)
                .foregroundColor(.secondary)

            HStack(spacing: -8) {
                ForEach(reservation.participants.prefix(5)) { participant in
                    if let avatarUrl = participant.user.avatarUrl, let url = URL(string: avatarUrl) {
                        AsyncImage(url: url) { image in
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                        } placeholder: {
                            Circle()
                                .fill(Color.gray.opacity(0.3))
                        }
                        .frame(width: 28, height: 28)
                        .clipShape(Circle())
                        .overlay(
                            Circle()
                                .stroke(Color.white, lineWidth: 2)
                        )
                    }
                }

                if reservation.participants.count > 5 {
                    Text("+\(reservation.participants.count - 5)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.leading, 8)
                }
            }
        }
        .padding(.vertical, 4)
    }

    private var statusColor: Color {
        switch reservation.status {
        case .confirmed:
            return .green
        case .pending:
            return .orange
        case .cancelled:
            return .red
        }
    }
}

struct ReservationDetailView: View {
    let reservation: Reservation
    let onAccept: () async -> Void
    @EnvironmentObject var sessionViewModel: SessionViewModel
    @State private var isAccepting = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(reservation.venue.name)
                        .font(.title)
                        .fontWeight(.bold)

                    HStack {
                        Image(systemName: "calendar")
                            .foregroundColor(.secondary)
                        Text(reservation.time, style: .date)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }

                    HStack {
                        Image(systemName: "clock")
                            .foregroundColor(.secondary)
                        Text(reservation.time, style: .time)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }

                    HStack {
                        Image(systemName: "location.fill")
                            .foregroundColor(.secondary)
                        Text(reservation.venue.address)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.horizontal)

                Divider()

                VStack(alignment: .leading, spacing: 12) {
                    Text("Participants")
                        .font(.headline)
                        .padding(.horizontal)

                    ForEach(reservation.participants) { participant in
                        HStack {
                            if let avatarUrl = participant.user.avatarUrl, let url = URL(string: avatarUrl) {
                                AsyncImage(url: url) { image in
                                    image
                                        .resizable()
                                        .aspectRatio(contentMode: .fill)
                                } placeholder: {
                                    Circle()
                                        .fill(Color.gray.opacity(0.3))
                                }
                                .frame(width: 40, height: 40)
                                .clipShape(Circle())
                            } else {
                                Circle()
                                    .fill(Color.blue.opacity(0.3))
                                    .frame(width: 40, height: 40)
                            }

                            Text(participant.user.name)
                                .font(.subheadline)

                            Spacer()

                            Text(participant.status.rawValue.capitalized)
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(participantStatusColor(participant.status).opacity(0.2))
                                .foregroundColor(participantStatusColor(participant.status))
                                .cornerRadius(8)
                        }
                        .padding(.horizontal)
                    }
                }

                if let userId = sessionViewModel.currentUser?.id,
                   let myParticipation = reservation.participants.first(where: { $0.userId == userId }),
                   myParticipation.status == .invited {
                    Button {
                        Task {
                            isAccepting = true
                            await onAccept()
                            isAccepting = false
                        }
                    } label: {
                        HStack {
                            if isAccepting {
                                ProgressView()
                                    .tint(.white)
                            } else {
                                Image(systemName: "checkmark.circle.fill")
                                Text("Accept Invitation")
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .disabled(isAccepting)
                    .padding(.horizontal)
                }
            }
            .padding(.vertical)
        }
        #if os(iOS)
        .navigationBarTitleDisplayMode(.inline)
        #endif
    }

    private func participantStatusColor(_ status: ParticipantStatus) -> Color {
        switch status {
        case .accepted:
            return .green
        case .invited:
            return .orange
        case .declined:
            return .red
        }
    }
}
