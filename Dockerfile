# syntax = docker/dockerfile:1

# Adjust NODE_VERSION as desired
ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-slim AS base
LABEL fly_launch_runtime="Node.js"

# Enable PNPM
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

COPY . /app
# Node.js app lives here
WORKDIR /app

ENV NODE_ENV="production"

# Install packages needed to build node modules
RUN apt-get update -qq && \
  apt-get install -y build-essential pkg-config python-is-python3

# Install node modules
FROM base AS prod-deps
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile
FROM base AS build
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile --prod=false
# Build application
RUN pnpm run build

FROM base
# Copy built application
COPY --from=prod-deps /app/node_modules /app/node_modules
COPY --from=build /app/dist /app/dist
# Start the server by default, this can be overwritten at runtime
EXPOSE 3000
CMD [ "pnpm", "start" ]
