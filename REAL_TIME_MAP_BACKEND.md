 # Real-Time Map Backend Architecture

 ## APIs

 1. **GET /api/map_nodes**
    - Returns all visible users (map nodes) within a given area or radius.
    - Query params: `lat`, `lng`, `radius`, optional filters (e.g. `role`).
    - Enforces auth & visibility (location sharing, visible_roles).

    Example:
    ```http
    GET /api/map_nodes?lat=25.2048&lng=55.2708&radius=500 HTTP/1.1
    Authorization: Bearer <token>
    ```

 2. **GET /api/search** — Standard name/role/keyword search. Params: `query`, `role`, pagination.

 3. **POST /api/ai_search** — Proxied AI matchmaking. Body: `{ "prompt": "..." }`.

 4. **POST /api/location** — HTTP fallback for `location_update` WS. Body `{ lat,lng,timestamp }`.

 5. **POST /api/meet_now** — Creates MeetNowRequest; Body `{ target_user_id, message }`.

 6. **POST /api/request_introduction** — Creates IntroductionRequest; Body `{ target_user_id,via_user_id,message }`.

 7. **GET /api/meetups** — List upcoming/active meetups for the user.

 8. **GET /api/notifications** — Paginated notifications; filter `?unread=true`.

 9. **POST /api/notifications/mark_read** — Marks notifications read; Body: `{ notification_ids: [] }`.

 10. **GET/PUT /api/settings** — Fetch/update user preferences (location_sharing, visible_roles, filters).

 ## WebSocket Events

 - **location_update** (C→S): `{ event: 'location_update', data: { lat, lng, timestamp }}`
 - **user_location** (S→C): broadcast of peers' locations.
 - **meet_request** (S→C): resume pending meet-now invites.
 - **introduction_request** (S→C): invites to facilitate intros.
 - **meetup_update** (S↔C): live meetup updates (position, chat).
 - **notification** (S→C): generic, stored in DB.
 - **presence_update** (S→C): online/offline/visibility.

 ## Data Models

 - **User**: user_id, name, roles[], current_lat, current_lng, location_updated_at, location_sharing, visible_roles[], profile fields.
 - **MeetNowRequest**: id, from_user_id, to_user_id, message, status, created_at, updated_at.
 - **IntroductionRequest**: id, from_user_id, to_user_id, via_user_id, status, created_at, updated_at.
 - **Meetup**: id, organizer_id, participant_ids[], location, time, status.
 - **Notification**: id, user_id, type, content, related_id, is_read, created_at.
 - **Settings**: user_id, location_sharing, visible_roles[], filters {}.
 - (_Opt_) **LocationHistory**: id, user_id, lat, lng, timestamp.

 ## Privacy & Permissions

 - Authenticate all REST & WS (JWT/session).
 - Filter map/search by location_sharing & visible_roles.
 - Respect user filters (show_roles).
 - Enforce TLS, sanitize inputs, log access.

 ## Scaling Strategy

 - Distributed WS servers + Redis/Kafka pubsub.
 - Sharded DB with geospatial indexing & caching.
 - Rate-limiting & debouncing for high-frequency updates.
 - Stateless servers with shared session store.
 - Monitoring, autoscaling, health checks.

 ## Additional Notes

 - **AI Integration**: server-side `/api/ai_search` proxy using env `OPENAI_API_KEY`.
 - **Role Filtering**: backend-only enforcement.
 - **Notifications**: WS realtime + REST fallback.
 - **Meetup Coordination**: private WS channel per meetup.
 - **Security**: env var secrets, parameterized queries, least privilege.
 - **Observability**: logging, metrics, tracing.