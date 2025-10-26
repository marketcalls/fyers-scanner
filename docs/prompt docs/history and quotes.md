Here’s the **Fyers Data API documentation** (History & Quotes) reformatted into a clean, developer-friendly **Markdown** file — including your provided **curl examples** and **sample success responses**.

---

# 📘 FYERS Data API Documentation

## Overview

The Fyers **Data API** provides access to **historical** and **real-time quote data** across multiple exchanges.
It supports different time resolutions and returns data in standardized JSON format for easy consumption in trading and analytics applications.

---

## 🕒 1. Historical Data API (`/data/history`)

### **Endpoint**

```
GET https://api-t1.fyers.in/data/history
```

### **Description**

Retrieves archived historical data for a given symbol in multiple resolutions (minute, hourly, daily, etc.).

---

### **Request Parameters**

| Parameter     | Type   | Required | Description                                                                                        |
| ------------- | ------ | -------- | -------------------------------------------------------------------------------------------------- |
| `symbol`      | string | ✅        | Trading symbol in the format `EXCHANGE:SYMBOL`. <br>Example: `NSE:SBIN-EQ`                         |
| `resolution`  | string | ✅        | Candle resolution. <br>Possible values: `1, 2, 3, 5, 10, 15, 20, 30, 45, 60, 120, 180, 240, D, 1D` |
| `date_format` | int    | ✅        | Format of date input. <br>`0` → epoch time, `1` → `YYYY-MM-DD`                                     |
| `range_from`  | string | ✅        | Start date or epoch value (based on `date_format`)                                                 |
| `range_to`    | string | ✅        | End date or epoch value (based on `date_format`)                                                   |
| `cont_flag`   | int    | ❌        | Set to `1` for continuous data (F&O)                                                               |
| `oi_flag`     | int    | ❌        | Set to `1` to include open interest (OI) data                                                      |

---

### **Example cURL Request**

```bash
curl --location --request GET \
'https://api-t1.fyers.in/data/history?symbol=NSE:SBIN-EQ&resolution=30&date_format=1&range_from=2021-01-01&range_to=2021-01-02&cont_flag=' \
--header 'Authorization: app_id:access_token'
```

---

### **Sample Success Response**

```json
{
  "s": "ok",
  "candles": [
    [1621814400, 417.0, 419.2, 405.3, 412.05, 142964052],
    [1621900800, 415.1, 415.5, 408.5, 412.35, 56048127],
    [1621987200, 413.8, 418.75, 410.8, 413.55, 52357719],
    [1622073600, 413.7, 429.1, 412.0, 425.2, 73392997]
  ]
}
```

---

### **Response Fields**

| Field     | Type   | Description                            |
| --------- | ------ | -------------------------------------- |
| `s`       | string | Status (`ok` or `error`)               |
| `candles` | array  | List of arrays representing OHLCV data |
| → [0]     | int    | Epoch timestamp                        |
| → [1]     | float  | Open price                             |
| → [2]     | float  | High price                             |
| → [3]     | float  | Low price                              |
| → [4]     | float  | Close price                            |
| → [5]     | int    | Volume traded                          |

---

### **Notes**

* For complete candles, ensure `range_to` is **one minute before** the current time.
* Data availability:

  * Up to **100 days per request** for intraday resolutions.
  * Up to **366 days** for daily (`1D`) resolution.
  * Data available from **July 3, 2017**.
* **Unlimited symbols** can be queried per day.

---

## 💹 2. Quotes API (`/data/quotes`)

### **Endpoint**

```
GET https://api-t1.fyers.in/data/quotes
```

### **Description**

Retrieves live market quote data for one or more symbols.

---

### **Request Parameters**

| Parameter | Type   | Required | Description                                                                              |
| --------- | ------ | -------- | ---------------------------------------------------------------------------------------- |
| `symbols` | string | ✅        | Comma-separated list of up to **50 symbols**. <br>Example: `NSE:SBIN-EQ,BSE:RELIANCE-EQ` |

---

### **Example cURL Request**

```bash
curl --location --request GET \
'https://api-t1.fyers.in/data/quotes?symbols=NSE:SBIN-EQ' \
--header 'Authorization: app_id:access_token'
```

---

### **Sample Success Response**

```json
{
  "s": "ok",
  "code": 200,
  "d": [
    {
      "n": "NSE:SBIN-EQ",
      "s": "ok",
      "v": {
        "ch": 1.7,
        "chp": 0.4,
        "lp": 426.9,
        "spread": 0.05,
        "ask": 426.9,
        "bid": 426.85,
        "open_price": 430.5,
        "high_price": 433.65,
        "low_price": 423.6,
        "prev_close_price": 425.2,
        "atp": 428.07,
        "volume": 38977242,
        "short_name": "SBIN-EQ",
        "exchange": "NSE",
        "description": "NSE:SBIN-EQ",
        "original_name": "NSE:SBIN-EQ",
        "symbol": "NSE:SBIN-EQ",
        "fyToken": "10100000003045",
        "tt": "1622160000"
      }
    }
  ]
}
```

---

### **Response Fields**

| Field                | Type   | Description                    |
| -------------------- | ------ | ------------------------------ |
| `s`                  | string | Status (`ok` or `error`)       |
| `code`               | int    | Response code                  |
| `d`                  | array  | List of quote objects          |
| `v.ch`               | float  | Change in price                |
| `v.chp`              | float  | Percentage change              |
| `v.lp`               | float  | Last traded price              |
| `v.ask`              | float  | Asking price                   |
| `v.bid`              | float  | Bidding price                  |
| `v.open_price`       | float  | Opening price                  |
| `v.high_price`       | float  | Highest price                  |
| `v.low_price`        | float  | Lowest price                   |
| `v.prev_close_price` | float  | Previous closing price         |
| `v.atp`              | float  | Average traded price           |
| `v.volume`           | int    | Volume traded                  |
| `v.short_name`       | string | Short name of symbol           |
| `v.exchange`         | string | Exchange name                  |
| `v.fyToken`          | string | Unique identifier for symbol   |
| `v.tt`               | int    | Epoch timestamp of last update |

---

### **Rate Limits**

* Maximum **50 symbols** per request.
* Real-time updates depend on your Fyers API subscription tier.

---

Would you like me to export this as a **`Fyers_Data_API.md`** file so you can directly add it to your project docs folder (e.g., `docs/api/`)?
