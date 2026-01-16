import os
from pathlib import Path

WORKSPACE_ROOT = Path("c:/Users/nabhi/Downloads/python_elinity-main2")
GAMES_ROOT = WORKSPACE_ROOT / "elinity game suite"

DOCKERFILE_CONTENT = """# Builder Stage
FROM node:20-bullseye-slim AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Build time arg
ARG NEXT_PUBLIC_P1_BACKEND_URL
ENV NEXT_PUBLIC_P1_BACKEND_URL=${NEXT_PUBLIC_P1_BACKEND_URL}

RUN npm run build

# Runner Stage
FROM node:20-bullseye-slim AS runner
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
"""

NEXT_CONFIG_CONTENT = """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  eslint: {
    ignoreDuringBuilds: true,
  },
};
module.exports = nextConfig;
"""

def update_games():
    print(f"Scanning {GAMES_ROOT}...")
    games = [d for d in os.listdir(GAMES_ROOT) if (GAMES_ROOT / d).is_dir() and d.startswith("elinity")]
    
    print(f"Found {len(games)} games to update.")
    
    for game in games:
        game_path = GAMES_ROOT / game
        
        # Update Dockerfile
        dockerfile_path = game_path / "Dockerfile"
        # We overwrite blindly to ensure consistency
        dockerfile_path.write_text(DOCKERFILE_CONTENT, encoding='utf-8')
        print(f"Updated Dockerfile for {game}")
        
        # Update next.config.js
        next_config_path = game_path / "next.config.js"
        # We overwrite blindly to ensure consistency
        next_config_path.write_text(NEXT_CONFIG_CONTENT, encoding='utf-8')
        print(f"Updated next.config.js for {game}")

    print("Bulk update complete.")

if __name__ == "__main__":
    update_games()
