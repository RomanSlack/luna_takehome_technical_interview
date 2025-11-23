# Luna Video Walkthrough Script
**Target Duration: 7 minutes**

---

## Opening (0:00 - 0:30)

**[Slide 1: Title]**

> "Hi, I'm Roman, and this is my submission for the Luna technical interview. I've built a full-stack social venue discovery platform that helps people connect through shared interests in places they want to visit."

**[Slide 2: Overview]**

> "The project uses SwiftUI for iOS, Flask for the web frontend, FastAPI for the backend, PostgreSQL for data, and everything runs in Docker. Let me walk you through what I built."

---

## Tracks Completed (0:30 - 1:15)

**[Slide 3: Tracks]**

> "I completed all three tracks: Track 1 is the iOS frontend using MVVM architecture. Track 2 is the backend with a recommendation engine and AI agents. Track 3 ties it all together with full-stack integration. As a bonus, I also built a Flask web frontend with complete feature parity."

**[Slide 4: iOS Frontend]**

> "The iOS app follows MVVM strictly - all ViewModels use @Published properties and Combine for reactive updates. The networking layer uses modern async/await, and I've implemented clean separation between views, view models, and models."

---

## Backend Deep Dive (1:15 - 3:00)

**[Slide 5: Recommendation Engine]**

> "The recommendation engine has two core components. First is spatial analysis - I implemented Haversine distance calculations for accurate geolocation. Venues closer to you get exponentially higher scores. Second is social compatibility - the system considers friendship strength, shared venue interests, and whether your friends are also interested in specific venues."

**[Slide 6: AI Agents]**

> "The AI agent system monitors user interest confirmations in real-time. When two or more users confirm they want to go to the same venue, the agent automatically creates a reservation for tomorrow at 7 PM. It prevents duplicates by checking 30-minute time windows and seamlessly coordinates group bookings without any manual effort."

**[Slide 7: Architecture]**

> "The architecture uses a clean layered approach. FastAPI handles all backend logic with proper service layers. SQLAlchemy provides the ORM, and Pydantic validates all inputs. Everything is containerized with Docker Compose, including health checks and hot reload for development."

---

## Features & Product Thinking (3:00 - 4:15)

**[Slide 8: Key Features]**

> "On the discovery side, users get personalized venue recommendations with match scores and can see which friends are interested. The social side shows recommended people for each venue with compatibility scores, making it easy to coordinate group outings."

**[Slide 10: Product-Market Fit]**

> "From a product perspective, this hits three key points. Intuitive usability through clean UI and instant onboarding. Social growth because seeing your friends' interests naturally encourages invitations. And utility value - automated reservations remove friction from the booking process. The more users join, the better the recommendations get, creating strong network effects."

---

## Technical Excellence (4:15 - 5:00)

**[Slide 9: Metrics]**

> "By the numbers: over 3,000 lines of code across both frontends and backend, 20+ RESTful API endpoints, two fully functional frontends, and 100% Docker deployment."

**[Slide 13: Code Quality]**

> "Code quality was a priority. I used type hints throughout Python and Swift, implemented structured JSON logging with context, comprehensive error handling, unit tests for the recommendation algorithms, and followed RESTful best practices."

**[Slide 14: Development]**

> "I leveraged AI coding agents extensively - about 70-90% assistant generation across the stack - but I made all architectural decisions and did thorough code review. This is documented in the README as required."

---

## Live Demo (5:00 - 6:45)

**[Slide 15: Demo Time]**

> "Now let's see it in action."

**[Switch to running app - Web or iOS]**

### Demo Flow:

1. **User Selection** (0:10)
   > "First, users can select which account to view. This demonstrates the personalization."

2. **Discover Tab** (0:20)
   > "Here's the discover feed with personalized recommendations. Notice the match scores - higher means better fit based on location and social signals. You can see friend avatars showing who's interested in each venue."

3. **Venue Detail** (0:20)
   > "Clicking a venue shows details and recommended people. The compatibility bars show how well-matched you are with each friend for this specific venue."

4. **Confirm Interest** (0:15)
   > "When I click 'Confirm Going', it saves my interest. Let me switch to another user and confirm the same venue..."

5. **Auto-Reservation** (0:20)
   > "Now check the My Plans tab - the AI agent detected both confirmations and automatically created a reservation with both participants. This is the seamless automation in action."

6. **Reservation Management** (0:15)
   > "Users can view all participants, see status, and cancel plans if needed."

7. **Profile** (0:15)
   > "The profile shows friends with relationship strength and all your interests."

**[Back to slides]**

---

## Closing (6:45 - 7:00)

**[Slide 16: Thank You]**

> "That's Luna - a complete full-stack solution with production-quality code, thoughtful architecture, and real product thinking. The GitHub repo has comprehensive documentation, setup instructions, and all the code. Thank you for watching, and I'm excited to discuss this further!"

---

## Backup Talking Points

If you have extra time or need to fill gaps:

- **Flask Frontend:** "The web version has 100% feature parity and works on any device - great for testing and broad accessibility."
- **Database Design:** "I used a relational model with proper foreign keys and cascading deletes for data integrity."
- **Testing:** "The backend has pytest tests for the recommendation algorithms, covering edge cases like no location data or no friends."
- **Deployment Ready:** "Everything is containerized and ready to deploy to Google Cloud Run with minimal changes."
- **Documentation:** "The README includes ASCII architecture diagrams, setup instructions, and detailed explanations of all design decisions."

---

## Recording Tips

- **Screen Setup:**
  - Browser with presentation: localhost presentation/index.html
  - App running: localhost:5000 or iOS Simulator
  - Terminal visible for docker ps (optional)

- **Timing Checkpoints:**
  - 2:00 mark: Should be finishing AI agents
  - 4:00 mark: Should be starting metrics/code quality
  - 5:00 mark: Should be starting live demo
  - 6:45 mark: Should be on thank you slide

- **Energy:**
  - Smile and sound enthusiastic
  - Use hand gestures (if on camera)
  - Vary your pace - speed up for easy parts, slow down for complex concepts
  - Show genuine excitement about cool features

- **If Running Over Time:**
  - Skip slides 11-12 (Flask bonus, data model)
  - Keep demo under 1:30
  - Combine slides 13-14

- **If Running Under Time:**
  - Add API documentation demo (localhost:8000/docs)
  - Show docker-compose logs
  - Discuss future enhancements

Good luck! 🎬
