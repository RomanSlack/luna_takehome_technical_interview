import Foundation

enum ReservationStatus: String, Codable {
    case pending = "PENDING"
    case confirmed = "CONFIRMED"
    case cancelled = "CANCELLED"
}

enum ParticipantStatus: String, Codable {
    case invited = "INVITED"
    case accepted = "ACCEPTED"
    case declined = "DECLINED"
}

struct ReservationParticipant: Codable, Identifiable, Hashable {
    let id: Int
    let userId: Int
    let status: ParticipantStatus
    let user: User

    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case status
        case user
    }
}

struct Reservation: Codable, Identifiable, Hashable {
    let id: Int
    let venueId: Int
    let createdByUserId: Int
    let time: Date
    let status: ReservationStatus
    let createdAt: Date
    let venue: Venue
    let participants: [ReservationParticipant]

    enum CodingKeys: String, CodingKey {
        case id
        case venueId = "venue_id"
        case createdByUserId = "created_by_user_id"
        case time
        case status
        case createdAt = "created_at"
        case venue
        case participants
    }
}

struct ReservationCreate: Codable {
    let venueId: Int
    let time: Date
    let participantUserIds: [Int]

    enum CodingKeys: String, CodingKey {
        case venueId = "venue_id"
        case time
        case participantUserIds = "participant_user_ids"
    }
}

struct ReservationAccept: Codable {
    let reservationId: Int
    let userId: Int

    enum CodingKeys: String, CodingKey {
        case reservationId = "reservation_id"
        case userId = "user_id"
    }
}

struct AgentResult: Codable {
    let success: Bool
    let message: String
    let reservation: Reservation?
}
