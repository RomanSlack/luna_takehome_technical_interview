import Foundation

struct RecommendedPerson: Codable, Identifiable, Hashable {
    let user: User
    let compatibilityScore: Double

    var id: Int { user.id }

    enum CodingKeys: String, CodingKey {
        case user
        case compatibilityScore = "compatibility_score"
    }
}

struct RecommendedVenue: Codable, Identifiable, Hashable {
    let venue: Venue
    let score: Double
    let recommendedPeople: [RecommendedPerson]

    var id: Int { venue.id }

    enum CodingKeys: String, CodingKey {
        case venue
        case score
        case recommendedPeople = "recommended_people"
    }
}

struct RecommendationsResponse: Codable {
    let recommendedVenues: [RecommendedVenue]

    enum CodingKeys: String, CodingKey {
        case recommendedVenues = "recommended_venues"
    }
}
