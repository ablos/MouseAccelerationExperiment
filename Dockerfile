FROM node:22-alpine AS builder
RUN apk upgrade --no-cache
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run prepare && npm run build

FROM node:22-alpine
RUN apk upgrade --no-cache
WORKDIR /app
COPY --from=builder /app/build build/
COPY --from=builder /app/node_modules node_modules/
COPY package.json .
EXPOSE 3000
ENV NODE_ENV=production
CMD ["node", "build"]
