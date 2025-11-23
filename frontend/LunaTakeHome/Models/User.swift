import Foundation

struct User: Identifiable, Codable, Hashable {
    let id: Int
    let name: String
    let avatarUrl: String?
    let bio: String?

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case avatarUrl = "avatar_url"
        case bio
    }
}

struct UserCreate: Codable {
    let name: String
    let avatarUrl: String?
    let bio: String?

    enum CodingKeys: String, CodingKey {
        case name
        case avatarUrl = "avatar_url"
        case bio
    }
}
