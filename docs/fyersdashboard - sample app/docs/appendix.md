Here’s your **Fyers Appendix** converted into a clean, separate **Markdown document** — ideal for reference in API documentation or developer portals.

---

# 📘 Fyers API Appendix

This appendix provides reference tables for **symbol formats**, **exchange codes**, **product types**, **order types**, and related constants used across the **Fyers API**.

---

## 🔹 FYToken Structure

| Component          | Length     | Description                    | Example  |
| ------------------ | ---------- | ------------------------------ | -------- |
| **Exchange**       | 2 digits   | Exchange code                  | `10`     |
| **Segment**        | 2 digits   | Segment code                   | `11`     |
| **Expiry**         | 6 digits   | Format: YYMMDD                 | `200827` |
| **Exchange Token** | 2–6 digits | Token assigned by the exchange | `22`     |

---

## 🔹 Exchanges

| Value | Exchange Name                  |
| ----- | ------------------------------ |
| `10`  | NSE (National Stock Exchange)  |
| `11`  | MCX (Multi Commodity Exchange) |
| `12`  | BSE (Bombay Stock Exchange)    |

---

## 🔹 Segments

| Value | Segment Name          |
| ----- | --------------------- |
| `10`  | Capital Market        |
| `11`  | Equity Derivatives    |
| `12`  | Currency Derivatives  |
| `20`  | Commodity Derivatives |

---

## 🔹 Available Exchange–Segment Combinations

| Exchange | Segment               | Exchange Code | Segment Code |
| -------- | --------------------- | ------------- | ------------ |
| NSE      | Capital Market        | 10            | 10           |
| NSE      | Equity Derivatives    | 10            | 11           |
| NSE      | Currency Derivatives  | 10            | 12           |
| NSE      | Commodity Derivatives | 10            | 20           |
| BSE      | Capital Market        | 12            | 10           |
| BSE      | Equity Derivatives    | 12            | 11           |
| BSE      | Currency Derivatives  | 12            | 12           |
| MCX      | Commodity Derivatives | 11            | 20           |

---

## 🔹 Instrument Types

| Segment | Code      | Description                    |
| ------- | --------- | ------------------------------ |
| **CM**  | 0         | EQ (Equity)                    |
|         | 1         | Preference Shares              |
|         | 2         | Debentures                     |
|         | 3         | Warrants                       |
|         | 4         | Misc (NSE, BSE)                |
|         | 5         | SGB                            |
|         | 6         | G-Secs                         |
|         | 7         | T-Bills                        |
|         | 8         | Mutual Funds                   |
|         | 9         | ETFs                           |
|         | 10        | Index                          |
|         | 50        | Misc (BSE)                     |
| **FO**  | 11        | FUTIDX                         |
|         | 12        | FUTIVX                         |
|         | 13        | FUTSTK                         |
|         | 14        | OPTIDX                         |
|         | 15        | OPTSTK                         |
| **CD**  | 16–25     | FUTCUR, OPTCUR, UNDIRC, etc.   |
| **COM** | 11, 30–37 | FUTCOM, OPTCOM, FUTBLN, OPTBLN |

---

## 🔹 Symbology Format

| Segment                     | Format                                                    | Examples                   |
| --------------------------- | --------------------------------------------------------- | -------------------------- |
| Equity                      | `{Ex}:{Ex_Symbol}-{Series}`                               | `NSE:SBIN-EQ`, `BSE:ACC-A` |
| Equity Futures              | `{Ex}:{Ex_UnderlyingSymbol}{YY}{MMM}FUT`                  | `NSE:NIFTY20OCTFUT`        |
| Equity Options (Monthly)    | `{Ex}:{Ex_UnderlyingSymbol}{YY}{MMM}{Strike}{Opt_Type}`   | `NSE:NIFTY20OCT11000CE`    |
| Equity Options (Weekly)     | `{Ex}:{Ex_UnderlyingSymbol}{YY}{M}{dd}{Strike}{Opt_Type}` | `NSE:NIFTY20O812000CE`     |
| Currency Futures            | `{Ex}:{Ex_CurrencyPair}{YY}{MMM}FUT`                      | `NSE:USDINR20OCTFUT`       |
| Currency Options (Monthly)  | `{Ex}:{Ex_CurrencyPair}{YY}{MMM}{Strike}{Opt_Type}`       | `NSE:USDINR20OCT75CE`      |
| Currency Options (Weekly)   | `{Ex}:{Ex_CurrencyPair}{YY}{M}{dd}{Strike}{Opt_Type}`     | `NSE:USDINR20N0580.5PE`    |
| Commodity Futures           | `{Ex}:{Ex_Commodity}{YY}{MMM}FUT`                         | `MCX:GOLD20DECFUT`         |
| Commodity Options (Monthly) | `{Ex}:{Ex_Commodity}{YY}{MMM}{Strike}{Opt_Type}`          | `MCX:CRUDEOIL20OCT4000CE`  |

---

## 🔹 Symbology Variables

| Variable     | Description                   | Possible Values       |
| ------------ | ----------------------------- | --------------------- |
| `{Ex}`       | Exchange code                 | NSE, BSE, MCX         |
| `{YY}`       | Last two digits of year       | 19, 20, 21, 22        |
| `{MMM}`      | Month (3-letter uppercase)    | JAN, FEB, MAR, …, DEC |
| `{M}`        | Weekly expiry month shorthand | 1–9, O, N, D          |
| `{dd}`       | Day of month (2 digits)       | 01–31                 |
| `{Opt_Type}` | Option type                   | CE (Call), PE (Put)   |
| `{Strike}`   | Option strike price           | 11000, 75.5           |

---

## 🔹 Product Types

| Value      | Description                     |
| ---------- | ------------------------------- |
| `CNC`      | For equity only                 |
| `INTRADAY` | Applicable for all segments     |
| `MARGIN`   | Applicable only for derivatives |
| `CO`       | Cover Order                     |
| `BO`       | Bracket Order                   |
| `MTF`      | Margin Trading Facility         |

---

## 🔹 Order Types

| Value | Description            |
| ----- | ---------------------- |
| `1`   | Limit Order            |
| `2`   | Market Order           |
| `3`   | Stop Order (SL-M)      |
| `4`   | Stoplimit Order (SL-L) |

---

## 🔹 Order Status

| Value | Description     |
| ----- | --------------- |
| `1`   | Cancelled       |
| `2`   | Traded / Filled |
| `3`   | For future use  |
| `4`   | Transit         |
| `5`   | Rejected        |
| `6`   | Pending         |

---

## 🔹 Order Sides

| Value | Description |
| ----- | ----------- |
| `1`   | Buy         |
| `-1`  | Sell        |

---

## 🔹 Position Sides

| Value | Description     |
| ----- | --------------- |
| `1`   | Long            |
| `-1`  | Short           |
| `0`   | Closed position |

---

## 🔹 Holding Types

| Value | Description                              |
| ----- | ---------------------------------------- |
| `T1`  | Purchased but not yet delivered to demat |
| `HLD` | Shares available in demat account        |

---

## 🔹 Order Sources

| Code  | Description |
| ----- | ----------- |
| `M`   | Mobile      |
| `W`   | Web         |
| `R`   | Fyers One   |
| `A`   | Admin       |
| `ITS` | API         |

---

Would you like me to add **Quick Reference Tables** (e.g., “NIFTY Weekly Option Examples” and “MCX Commodity Futures Symbols”) to make this appendix more beginner-friendly for traders?
