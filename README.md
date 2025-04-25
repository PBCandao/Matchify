# Matchify

The Match-Everything Environment

Matchify is a match-everything, match-everyone social experience. Its very first product is a dynamic social-graph visualization, but that graph is merely the tip of the iceberg. Under the hood, Matchify is a universal matchmaking engine designed to connect people, ideas and opportunities in any domain.

1. Purpose & Vision

Empower Serendipity at Scale
We believe great things happen when the right people meet—whether they’re investors and founders, mentors and mentees, collaborators and creators. Our mission is to make these serendipitous matches inevitable.

Match Everything, Everyone
From phone-book contacts to professional roles to shared interests or geographic proximity, Matchify will one day link you to anything or anyone—customers, co-founders, service providers, event attendees—across a single unified network.

Privacy-First Discovery
True serendipity can’t come at the cost of privacy. We only reveal what you’ve consented to: locked connections stay blurred until you’re introduced, and no raw phone numbers or personal data ever leave your device.

2. Benefits & Goals

Instant Onboarding
No forms to fill. Upload your address book (vCard/CSV) or use your device’s contact picker; Matchify instantly identifies which of your contacts are already on the platform.

Role & Interest Clustering
Tag yourself (Investor, Developer, Designer, etc.) and watch your network organize itself around shared expertise—so you can zero-in on the opportunities that matter most.

Six-Degree Introductions
Go beyond your direct circle. Discover colleagues or collaborators up to six hops away, then request introductions through mutual friends—each step requires explicit approval, preserving trust.

Real-Time Dynamic Updates
As people join, connect or unlock new areas of the network, you see it live—in your browser—thanks to WebSockets driving instantaneous graph refreshes.

Seamless Off-Platform Chat
We focus on connection, not on building yet another chat system. Once introduced, each profile links to your Telegram handle so you can move the conversation into an environment you already trust.

Extensible Platform
Today it’s a social graph, tomorrow it’s skills matching, group discovery, marketplace integration—or any “match” scenario you can imagine. Our modular backend + embeddable frontend makes new use-cases easy to bolt on.

3. What Your Users Experience

Upload & Discover
Click “Import Contacts,” choose your vCard/CSV (or pick contacts in-browser). Instantly see which friends are on Matchify—no phone numbers ever stored in the clear.

Visualize Your Network
A force-directed D3.js graph blooms on-screen: circles for people, links for relationships, colored or clustered by role.

Explore & Unlock
Locked nodes at the graph’s edge pulse with potential. Click one to see it’s a “3rd-degree: Artist” via Alice → Bob. Hit “Request Introduction,” and Alice or Bob get a ping.

Consent & Connect
Each intermediary approves in turn. As they do, that node un-blurs and a new edge snaps into the graph—no page reload needed.

Move to Telegram
Once connected, tap “Chat on Telegram” on their profile modal. Matches ignite in an app you already use.

4. Technical High-Level Highlights

Contact Matching
Phone numbers are normalized (E.164) and SHA-256 hashed on-device. Only these hashes travel to our Python backend for fast, privacy-preserving lookups.

Six-Degree Pathfinding
A breadth-first search (BFS) up to 6 hops identifies introduction chains. Each link must explicitly approve before the next is unlocked.

Real-Time Graph Updates
A Flask + Flask-SocketIO server pushes graph_update and notification events. Our D3.js frontend listens on WebSockets and seamlessly incorporates diffs.

Modular Architecture
Backend code lives in backend/ (models.py, graph_logic.py, contacts.py, recommendations.py, notifications.py, fake_data.py). Frontend assets in frontend/ (index.html, graph.js, style.css).

First Product, Endless Potential
This repo ships Matchify’s social-graph demo. But the same matcher and API can power job platforms, lead gen tools, community finders, or any scenario where “matching” is the heart of the user experience.
