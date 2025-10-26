Here’s a clean **Markdown documentation** for only the **Fyers Place Order API** section — including request details, parameters, and the sample `curl` request and response.

---

# 💼 Fyers API v3 - Place Order

This API allows users to place a single order on any supported exchange via the **Fyers API v3** endpoint.

---

## **Endpoint**

```
POST https://api-t1.fyers.in/api/v3/orders/sync
```

---

## **Headers**

| Header          | Description                   |
| --------------- | ----------------------------- |
| `Authorization` | Format: `app_id:access_token` |
| `Content-Type`  | Must be `application/json`    |

---

## **Request Parameters**

| Parameter      | Type    | Description                                                                       |
| -------------- | ------- | --------------------------------------------------------------------------------- |
| `symbol`       | string  | Example: `MCX:SILVERMIC20NOVFUT`                                                  |
| `qty`          | int     | Quantity (must be in multiples of lot size for derivatives)                       |
| `type`         | int     | Order type:<br>1 = Limit<br>2 = Market<br>3 = Stop (SL-M)<br>4 = Stoplimit (SL-L) |
| `side`         | int     | 1 = Buy<br>-1 = Sell                                                              |
| `productType`  | string  | Order product type:<br>`CNC`, `INTRADAY`, `MARGIN`, `CO`, `BO`, `MTF`             |
| `limitPrice`   | float   | Price for Limit or Stoplimit orders; default = 0                                  |
| `stopPrice`    | float   | Price for Stop or Stoplimit orders; default = 0                                   |
| `validity`     | string  | `DAY` = Valid till market close<br>`IOC` = Immediate or Cancel                    |
| `disclosedQty` | int     | Default = 0 (applicable only for equity)                                          |
| `offlineOrder` | boolean | `false` = Normal order<br>`true` = AMO (After Market Order)                       |
| `stopLoss`     | float   | Applicable for CO and BO orders; default = 0                                      |
| `takeProfit`   | float   | Applicable for BO orders; default = 0                                             |
| `orderTag`     | string  | Optional order tag identifier (e.g., `"tag1"`)                                    |

---

## **Curl Example**

```bash
curl -H "Authorization:app_id:access_token" \
-H "Content-Type: application/json" \
-X POST \
-d '{
  "symbol":"MCX:SILVERMIC20NOVFUT",
  "qty":1,
  "type":2,
  "side":1,
  "productType":"INTRADAY",
  "limitPrice":0,
  "stopPrice":0,
  "validity":"DAY",
  "disclosedQty":0,
  "offlineOrder":false,
  "stopLoss":0,
  "takeProfit":0,
  "orderTag":"tag1"
}' https://api-t1.fyers.in/api/v3/orders/sync
```

---

## **Sample Success Response**

```json
{
  "s": "ok",
  "code": 1101,
  "message": "Order submitted successfully. Your Order Ref. No.808058117761",
  "id": "808058117761"
}
```

---

## **Response Fields**

| Field     | Type   | Description                                                                         |
| --------- | ------ | ----------------------------------------------------------------------------------- |
| `s`       | string | `"ok"` on success or `"error"` on failure                                           |
| `code`    | int    | Status code (e.g., `1101` = success, `201` = request received but not acknowledged) |
| `message` | string | Status message from the API                                                         |
| `id`      | string | Unique order reference number                                                       |

---

Would you like me to add **error response examples** (like invalid token, insufficient funds, or invalid symbol) to make this section more complete for developer documentation?
