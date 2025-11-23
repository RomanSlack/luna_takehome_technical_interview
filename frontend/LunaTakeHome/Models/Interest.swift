import Foundation

enum InterestStatus: String, Codable {
    case interested = "INTERESTED"
    case notInterested = "NOT_INTERESTED"
    case invited = "INVITED"
    case confirmed = "CONFIRMED"
}

struct UserInterest: Identifiable, Codable {
    let id: Int
    let userId: Int
    let venueId: Int
    let status: InterestStatus
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case venueId = "venue_id"
        case status
        case createdAt = "created_at"
    }
}

struct UserInterestCreate: Codable {
    let venueId: Int
    let status: InterestStatus

    enum CodingKeys: String, CodingKey {
        case venueId = "venue_id"
        case status
    }
}
