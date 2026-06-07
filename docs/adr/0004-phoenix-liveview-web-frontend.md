# Phoenix LiveView for Web Frontend

The web frontend is built with Phoenix LiveView (Elixir). It consumes the Python REST API like any other client — no Elixir/Python integration at the code level.

Chosen partly to gain Elixir experience, and partly because LiveView's model (server owns state, UI is a projection via WebSocket) is philosophically aligned with the thin-client architecture: the Python backend owns all game state, and LiveView is well-suited to rendering server-driven state with minimal client-side logic. LiveView also has first-class support for streaming, leaving the door open for streamed AI text in a future version.

The alternative considered was HTMX, which would have kept the stack to one language (Python). LiveView was preferred for the learning goal and the stronger real-time story.
