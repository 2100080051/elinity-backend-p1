# Elinity App - User Flow & Screen Mapping

## 📊 Screen Implementation Status

| Status | Meaning |
|--------|---------|
| ✅ | Implemented |
| ⚠️ | Partially Implemented |
| ❌ | Missing/Not Implemented |

---

## 🔁 GLOBAL ENTRY POINTS

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| Splash Screen | ⚠️ | `WelcomeScreen.tsx` | - (not in nav) |
| Login | ✅ | `Authentication.tsx` | `Auth` |
| Signup | ✅ | `AuthSignUpPage.tsx` | `AuthSignUpPage` |
| Mode Selection (Romantic/Leisure/Collaboration) | ❌ | - | - |
| Profile Details (Name, Image, Voice) | ⚠️ | `ProfileCreation.tsx` | - (not in nav) |
| AI Voice/Text Onboarding | ⚠️ | `OnBoardingScreenTwo.tsx` | `Onboardingtwo` |
| Home Screen | ✅ | `Home.tsx` | `Prompt` (via TabNavigator) |

---

## 🛠️ ONBOARDING FLOW

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| Onboarding Screen 1 (What is Elinity) | ✅ | `OnBoardingScreenOne.tsx` | `Onboarding` |
| Onboarding Screen 2 (Voice/Chat Q&A) | ✅ | `OnBoardingScreenTwo.tsx` | `Onboardingtwo` |
| Onboarding Screen 3 (Profile Building) | ✅ | `OnBoardingScreenThree.tsx` | `Onboardingthree` |
| Onboarding Screen 4 (Key Features) | ❌ | - | - |
| Mode Selection Screen | ❌ | - | - |
| Set Preferences Screen | ❌ | - | - |

---

## 🏡 USER HOME FLOW

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| Home Screen (Dynamic Greeting) | ✅ | `Home.tsx` | `Prompt` |
| Explore Recommendations | ✅ | `DailyRecommondation.tsx` | `DailyRecommendations` |
| Smart Life Book | ❌ | - | - |
| Relationship Suite | ✅ | `RelationShipHome.tsx` | `RelationShipHome` |
| AI Companion | ✅ | `ChatElinty.tsx` | `ChatEllinty` |
| Natural Language Search | ✅ | `NaturalLanguageSearch.tsx` | `NLPSearch` |
| Voice Journal | ✅ | `VoiceJournal.tsx` | `VoiceJournal` |
| Calendar / Rituals | ⚠️ | `CreateEvent.tsx` (component) | `CreateEvent` |
| Games Suite | ✅ | `GamesScreen.tsx` | `ConnectionGameSuite` |

---

## 💞 RELATIONSHIP SUITE FLOW

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| Relationship Dashboard | ✅ | `RelationShipDashBoard.tsx` | `RelationShipDashBoard` |
| Relationship Home | ✅ | `RelationShipHome.tsx` | `RelationShipHome` |
| Relationship Book/Journal | ❌ | - | - |
| Relationship Pad Screen | ✅ | `RelationshipPadScreen.tsx` | `RelationshipPadScreen` |
| Moodboard / Canvas | ✅ | `RelationShipCanvas.tsx` | - (not in nav) |
| Daily Photojournal | ❌ | - | - |
| Relationship Coaching | ✅ | `RelationShipCoaching.tsx` | `RelationShipCoaching` |

---

## 🧠 SELF-RELATION / SMART LIFE MODE

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| Smart Life Book | ❌ | - | - |
| Voice Journal | ✅ | `VoiceJournal.tsx` | `VoiceJournal` |
| AI Journal | ✅ | `AIJournal.tsx` | `AIJournal` |
| AI Companion | ✅ | `ChatElinty.tsx` | `ChatEllinty` |
| Personal Sanctuary | ✅ | `PersonalSanctuary.tsx` | `PersonalSanctuary` |
| Personal Coaching & Therapy | ✅ | `PersonalCoachingAndTherapy.tsx` | `AICoach` |
| Deep Thinking (Reflection) | ✅ | `DeepThinkingWithReflection.tsx` | - (not in nav) |
| Deep Thinking (Session) | ✅ | `DeepThinkingWithSession.tsx` | - (not in nav) |
| Reflection | ✅ | `Reflection.tsx` | - (not in nav) |
| Socratic Dialogue | ✅ | `SocraticDialogueWithAI.tsx` | - (not in nav) |
| Journal Prompt | ✅ | `JournalPrompt.tsx` | - (not in nav) |

---

## 💬 MATCHING & SEARCH FLOW

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| Natural Language Search | ✅ | `NaturalLanguageSearch.tsx` | `NLPSearch` |
| Natural Language Results | ✅ | `NaturalLanguageResults.tsx` | `NLPResults` |
| Matches Screen | ✅ | `Matches.tsx` | `Matches` |
| Matches Results | ✅ | `MatchesResult.tsx` | - (not in nav) |
| Deep Profile View | ✅ | `DeepProfile.tsx` | `DeepProfile` |
| Romantic Profile | ✅ | `RomanticProfile.tsx` | - (not in nav) |
| Leisure Profile | ✅ | `LeistureProfile.tsx` | - (not in nav) |
| Collaborator Profile | ✅ | `CollaboratorProfile.tsx` | - (not in nav) |

---

## 🧩 CONNECTION & COMMUNICATION FLOW

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| Match Animation Screen | ❌ | - | - |
| Messaging / Chat | ✅ | `ChatScreen.tsx` | - (not in nav) |
| Messages Card | ✅ | `MessagesCard.tsx` | `MessagesCard` |
| Chat with Elinity | ✅ | `ChatElinty.tsx` | `ChatEllinty` |
| Video Call | ✅ | `VideoCall.tsx` | `VideoCall` |
| Games & Icebreakers | ✅ | `GamesScreen.tsx` | `ConnectionGameSuite` |
| Flirt or Fact Game | ✅ | `FlirtOrFactScreen.tsx` | - (not in nav) |

---

## 🗓️ SOCIAL & CALENDAR FLOW

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| Social Home | ✅ | `SocialHome.tsx` | `SocialHome` |
| Social Circle | ✅ | `SocialCircle.tsx` | `SocialCircle` |
| Create Event | ✅ | `CreateEvent.tsx` (component) | `CreateEvent` |
| Life Calendar | ❌ | - | - |
| Event RSVP | ❌ | - | - |
| Community | ✅ | `Community.tsx` | - (not in nav) |
| Community Blogs | ✅ | `CommunityBlogs.tsx` | - (not in nav) |
| Groups | ✅ | `Groups.tsx` | - (not in nav) |
| Create Groups | ✅ | `CreateGroups.tsx` | - (not in nav) |

---

## 🛠️ AI + PERSONALIZATION FLOW

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| AI Companion Customization | ❌ | - | - |
| Growth Screen | ✅ | `GrowthScreen.tsx` | - (not in nav) |
| Deep Connection | ✅ | `DeepConnection.tsx` | - (not in nav) |

---

## 🧠 ANALYTICS & INSIGHTS FLOW

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| AI Life Analysis | ❌ | - | - |
| AI Relationship Analysis | ❌ | - | - |
| Score Card | ✅ | `ScoreCard.tsx` | - (not in nav) |

---

## 💡 DAILY ENGAGEMENT FLOW

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| Daily Card | ⚠️ | `DailyRecommondation.tsx` | `DailyRecommendations` |
| Streaks | ✅ | `MyStreaks.tsx` | - (not in nav) |
| Nudges & Reminders | ✅ | `NudgesAndReminders.tsx` | - (not in nav) |
| Question Cards | ✅ | `QuestionCards.tsx` | `QuestionCards` |

---

## 🛒 PRICING & PAYMENTS

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| Pricing Page | ✅ | `Pricing.tsx` | - (not in nav) |
| Payment Screen | ✅ | `PaymentScreen.tsx` | `PaymentScreen` |

---

## 🎯 ADMIN & MISC

| Screen | Status | File | Route Name |
|--------|--------|------|------------|
| Settings | ✅ | `SettingScreen.tsx` | `SettingScreen` |
| Refer & Earn | ✅ | `ReferAndEarn.tsx` | `Referral` |
| Favourite Cards | ✅ | `FavouriteCards.tsx` | - (not in nav) |
| Timer/Soundtrack | ✅ | `TimerStyle.tsx`, `SoundTrackScreen.tsx` | - (not in nav) |
| People Screen | ✅ | `People.tsx` | - (not in nav) |
| Prompt Page | ✅ | `PromptPage.tsx` | - (used in TabNav) |

---

## ❌ MISSING SCREENS (Need Implementation)

### High Priority
1. **Mode Selection Screen** - Romantic / Leisure / Collaboration mode selector
2. **Onboarding Screen 4** - Key Features introduction
3. **Set Preferences Screen** - Relationship goals, partner traits, personality toggles
4. **Smart Life Book** - Main smart life pad with AI prompts
5. **Life Calendar** - Week/Month/Day views with events
6. **Match Animation Screen** - "It's a Match!" celebration screen

### Medium Priority
7. **Relationship Book/Journal** - Add journal entries with tags
8. **Daily Photojournal** - Photo timeline with favorites
9. **AI Life Analysis** - Weekly cognitive patterns, emotions, goals
10. **AI Relationship Analysis** - Relationship gaps and insights
11. **Event RSVP Screen** - Event attendance management
12. **AI Companion Customization** - Personality toggles, avatar generation

---

## 🔗 NAVIGATION ROUTES SUMMARY

### Currently Registered Routes (in AppNavigator.tsx):
1. `Onboarding` → OnBoardingScreenOne
2. `Onboardingtwo` → OnBoardingScreenTwo
3. `Onboardingthree` → OnBoardingScreenThree
4. `Auth` → AuthScreen
5. `AuthSignUpPage` → AuthSignUpPage
6. `Prompt` → MainWithDrawer (Home)
7. `VideoCall` → VideoCall
8. `DailyRecommendations` → DailyRecommendations
9. `RelationShipDashBoard` → RelationShipDashBoard
10. `SettingScreen` → SettingScreen
11. `RelationshipPadScreen` → RelationshipPadScreen
12. `SocialHome` → SocialHome
13. `RelationShipHome` → RelationShipHome
14. `QuestionCards` → QuestionCards
15. `MessagesCard` → MessagesCard
16. `SocialCircle` → SocialCircle
17. `RelationShipCoaching` → RelationShipCoaching
18. `VoiceJournal` → VoiceJournal
19. `AIJournal` → AIJournal
20. `DeepProfile` → DeepProfile
21. `AICoach` → PersonalCoachingAndTherapy
22. `PersonalSanctuary` → PersonalSanctuary
23. `Matches` → Matches
24. `NLPSearch` → NaturalLanguageSearch
25. `NLPResults` → NaturalLanguageResults
26. `ConnectionGameSuite` → GamesScreen
27. `Referral` → ReferAndEarn
28. `ChatEllinty` → ChatEllinty
29. `CreateEvent` → CreateEvent
30. `PaymentScreen` → PaymentScreen

### Screens NOT in Navigation (Need to be added):
- `WelcomeScreen`
- `ProfileCreation`
- `RelationShipCanvas`
- `DeepThinkingWithReflection`
- `DeepThinkingWithSession`
- `Reflection`
- `SocraticDialogueWithAI`
- `JournalPrompt`
- `MatchesResult`
- `RomanticProfile`
- `LeistureProfile`
- `CollaboratorProfile`
- `ChatScreen`
- `FlirtOrFactScreen`
- `Community`
- `CommunityBlogs`
- `Groups`
- `CreateGroups`
- `GrowthScreen`
- `DeepConnection`
- `ScoreCard`
- `MyStreaks`
- `NudgesAndReminders`
- `Pricing`
- `FavouriteCards`
- `TimerStyle`
- `SoundTrackScreen`
- `People`

---

## 📱 DRAWER MENU ROUTES

Current drawer menu items and their target routes:
1. Social Suite → `SocialSuite` (needs mapping)
2. Relationship Home → `RelationshipHome` (needs mapping)
3. My Sanctuary → `MySanctuary` (needs mapping)
4. Elinity Games Arena → `GamesArena` (needs mapping)
5. Lumi Chat → `LumiChat` (needs mapping)
6. Messages → `Messages` (needs mapping)
7. Notifications → `Notifications` (needs implementation)
8. Settings → `SettingScreen` ✅
9. Payments → `PaymentScreen` ✅
10. Referrals → `Referrals` (needs mapping)
11. SP → `SP` (needs implementation)
12. Deep User Profile → `DeepProfile` ✅

---

*Last Updated: December 10, 2025*
