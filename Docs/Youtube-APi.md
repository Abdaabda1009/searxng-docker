
# YouTube API Wrapper - v1.0.0

## Introduction

Welcome to the YouTube API Wrapper! This is a production-ready API that provides a powerful and simplified interface for searching YouTube. It is designed to be compatible with the SearXNG search engine structure, offering a robust and feature-rich experience for developers.

This document provides a detailed guide on how to use the available endpoints, parameters, and responses.

## Base URL

All API endpoints are relative to the following base URL:

```
https://youtube.nexalexica.com
```

---

## Endpoints

### 1. Search for Videos

This is the primary endpoint for searching for YouTube videos. It allows for flexible querying with pagination, filtering, and sorting.

-   **Endpoint:** `/api/youtube/search`
-   **Method:** `GET`
-   **Summary:** Search for YouTube videos based on a query string and optional filters.

#### Request Parameters

| Parameter          | Type    | In    | Required | Description                                                                | Default |
| ------------------ | ------- | ----- | -------- | -------------------------------------------------------------------------- | ------- |
| `q`                | string  | query | **Yes**  | The search query term (e.g., "funny animal videos").                       |         |
| `page`             | integer | query | No       | The page number for pagination. Must be `1` or greater.                    | `1`     |
| `results_per_page` | integer | query | No       | The number of results to return per page. Min: `1`, Max: `500`.            | `50`    |
| `duration`         | string  | query | No       | Filter videos by duration. Accepted values: `short`, `medium`, `long`.     | `null`  |
| `time_range`       | string  | query | No       | Filter videos by upload date. Accepted values: `today`, `this_week`, etc. | `null`  |
| `sort_by`          | string  | query | No       | The sorting order for the results. Accepted values: `relevance`, `rating`. | `null`  |

#### Example Request

Here is an example using `curl` to search for "tech reviews" and requesting the first page with 10 results.

```bash
curl -X GET "https://youtube.nexalexica.com/api/youtube/search?q=tech+reviews&page=1&results_per_page=10"
```

#### Example Success Response (`200 OK`)

```json
{
  "status": "success",
  "results": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Example Tech Review Video",
      "author": "Tech Reviewer",
      "channel_id": "UC-example-channel-ID",
      "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
      "length": "3:32",
      "views": "1.2B views",
      "publish_date": "2009-10-25",
      "description": "A deep dive into the latest gadget...",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
      "likes": "14000000",
      "channel_avatar": "https://yt3.ggpht.com/..."
    }
  ],
  "metadata": {
    "query": "tech reviews",
    "count": 10,
    "time": "0.452s",
    "engine": "youtube"
  },
  "suggestions": [
    "latest tech reviews",
    "smartphone reviews"
  ],
  "corrections": {}
}
```

---

### 2. Get Single Video Details

Retrieves the details for a single YouTube video by its unique ID.

-   **Endpoint:** `/api/youtube/video/{video_id}`
-   **Method:** `GET`
-   **Summary:** Get the full details for a specific video.

#### Request Parameters

| Parameter  | Type   | In   | Required | Description                        |
| ---------- | ------ | ---- | -------- | ---------------------------------- |
| `video_id` | string | path | **Yes**  | The unique 11-character YouTube video ID. |

#### Example Request

```bash
curl -X GET "https://youtube.nexalexica.com/api/youtube/video/dQw4w9WgXcQ"
```

#### Example Success Response (`200 OK`)

```json
{
  "status": "success",
  "result": {
    "video_id": "dQw4w9WgXcQ",
    "title": "Example Tech Review Video",
    "author": "Tech Reviewer",
    "channel_id": "UC-example-channel-ID",
    "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
    "length": "3:32",
    "views": "1.2B views",
    "publish_date": "2009-10-25",
    "description": "A deep dive into the latest gadget...",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "likes": "14000000",
    "channel_avatar": "https://yt3.ggpht.com/..."
  }
}
```

---

### 3. Health Check

A simple endpoint to verify that the API service is running and healthy.

-   **Endpoint:** `/api/youtube/health`
-   **Method:** `GET`
-   **Summary:** Provides a health status check for monitoring.

#### Example Request

```bash
curl -X GET "https://youtube.nexalexica.com/api/youtube/health"
```

#### Example Success Response (`200 OK`)

```json
{
  "status": "healthy",
  "timestamp": "2023-10-27T10:00:00.000Z"
}
```

---

### 4. Get API Configuration

Returns the current server-side configuration of the API wrapper, such as rate limits and result limits.

-   **Endpoint:** `/api/youtube/config`
-   **Method:** `GET`
-   **Summary:** Fetches the API's current configuration settings.

#### Example Request

```bash
curl -X GET "https://youtube.nexalexica.com/api/youtube/config"
```

#### Example Success Response (`200 OK`)

```json
{
  "max_results": 500,
  "timeout": 30,
  "rate_limit": {
    "requests": 1000,
    "window": 3600
  }
}
```

---

## Error Responses

If a request has invalid parameters, the API will return a `422 Unprocessable Entity` status code.

#### Example Validation Error (`422 Unprocessable Entity`)

This error occurs if a required parameter like `q` is missing from the search request.

```json
{
  "detail": [
    {
      "loc": [
        "query",
        "q"
      ],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```