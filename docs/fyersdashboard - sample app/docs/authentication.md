Here’s the **Fyers Authentication Guide** formatted in clean **Markdown** with both **Auth Step 1** and **Auth Step 2** curl requests and responses included.

---

# 🔐 Fyers API Authentication & Login Flow

This document explains how to authenticate with **Fyers API v3** and obtain your **access token** for subsequent requests.

---

## **Authentication Steps**

1. **Navigate to the Login API endpoint**
2. **After successful login**, the user is redirected to the `redirect_uri` with the `auth_code`
3. **POST** the `auth_code` and `appIdHash` (SHA-256 of `api_id:app_secret`) to the **Validate Authcode API** endpoint
4. **Obtain the access token** and use it for all subsequent API requests

---

## **Auth Step 1 – Generate Auth Code**

### **Endpoint**

```
GET https://api-t1.fyers.in/api/v3/generate-authcode
```

### **Request Parameters**

| Parameter       | Type   | Description                                                      |
| --------------- | ------ | ---------------------------------------------------------------- |
| `client_id`     | string | App ID received after app creation (e.g., `SPXXXXE7-100`)        |
| `redirect_uri`  | string | URL to redirect after successful login (must match app settings) |
| `response_type` | string | Must always be `"code"`                                          |
| `state`         | string | Random value returned after successful login for validation      |

---

### **Curl Example**

```bash
curl --location --request GET 'https://api-t1.fyers.in/api/v3/generate-authcode?client_id=SPXXXXE7-100&redirect_uri=https://trade.fyers.in/api-login/redirect-uri/index.html&response_type=code&state=sample_state'
```

---

### **Response Example**

```json
{
  "s": "ok",
  "code": 200,
  "message": "",
  "auth_code": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "state": "sample_state"
}
```

---

## **Auth Step 2 – Validate Auth Code**

Once you receive the `auth_code`, validate it to obtain your `access_token`.

### **Endpoint**

```
POST https://api-t1.fyers.in/api/v3/validate-authcode
```

### **Request Parameters**

| Parameter    | Type   | Description                          |
| ------------ | ------ | ------------------------------------ |
| `grant_type` | string | Must be `"authorization_code"`       |
| `appIdHash`  | string | SHA-256 of `api_id:app_secret`       |
| `code`       | string | The `auth_code` obtained from Step 1 |

---

### **Curl Example**

```bash
curl --location --request POST 'https://api-t1.fyers.in/api/v3/validate-authcode' \
--header 'Content-Type: application/json' \
--data-raw '{
    "grant_type":"authorization_code",
    "appIdHash":"c3efb1075ef2332b3a4ec7d44b0f05c1********************",
    "code":"eyJ0eXAi*******.eyJpc3MiOiJhcGkubG9********.r_65Awa1kGdsNTAgD******"
}'
```

---

### **Sample Success Response**

```json
{
  "s": "ok",
  "code": 200,
  "message": "",
  "access_token": "eyJ0eXAiOi***.eyJpc3MiOiJh***.HrSubihiFKXOpUOj_7***",
  "refresh_token": "eyJ0eXAiO***.eyJpc3MiOiJh***.67mXADDLrrleuEH_EE***"
}
```

---

## **Refresh Token**

When you validate the auth code, a **refresh token** is also issued.

* **Validity**: 15 days
* You can generate a new access token using this refresh token (as long as it is valid).

### **Parameters for Refresh Request**

| Parameter       | Type   | Description                           |
| --------------- | ------ | ------------------------------------- |
| `grant_type`    | string | Must be `"refresh_token"`             |
| `appIdHash`     | string | SHA-256 of `api_id:app_secret`        |
| `refresh_token` | string | Token received from the previous step |
| `pin`           | string | User’s trading PIN                    |

### **SHA-256 Reference Tool**

You can compute your `appIdHash` using this online tool:
👉 [https://emn178.github.io/online-tools/sha256.html](https://emn178.github.io/online-tools/sha256.html)

---

Would you like me to extend this markdown to include the **Refresh Token curl request** as well?
