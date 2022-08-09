![LoonaBilling](https://user-images.githubusercontent.com/28388670/172512382-81059cf6-c872-4a4c-a370-223f2d4d009c.png)

<img src="https://img.shields.io/discord/887501133902385202?logo=discord&style=social"> <img src="https://img.shields.io/github/last-commit/Loona-cc/LoonaBilling?logo=github&style=social"> <img src="https://img.shields.io/github/workflow/status/Loona-cc/LoonaBilling/CodeQL?logo=github-sponsors&style=social">

# Development Changelog (v1.9)
Sorry for the long wait for another update, had some problems with Stripe and the API.
Alot of the updates aren't documented

## Development TODO
+ Main
  + [ ] Backup System
    + [ ] Move Servers Easily
    + [ ] Online/Remote Backups
+ Payments
  + [x] Create Shopping Cart / Checkout (WIP)
  + [x] Create Customer Transaction Numbers (WIP) (Cart IDs)
  + [ ] Rework Payment Provider System
    + [x] Stripe (WIP)
    + [ ] PayPal (TODO)
+ Store
  + [ ] Make default be the default page (/store)
+ Products
  + [ ] Import Products from Payment Providers

## LoonaBilling
+ Changed encryption salt to ... instead of Mac Address (TODO)
  + Reason: Mac Address changes on different networks and will be a pain if servers change
+ Fixed Branding Issue
+ Added Error Handling for Admin Dashboard stats
+ Added Error Handling for Git Library

## Stripe
+ Rewrote Stripe Module
+ Added Automation
  + [x] Payments
  + [ ] Subscriptions (TODO)

## PayPal
+ Added PayPal (Needs to be reworked)

## Accounts
+ Added Settings Tab
+ 2FA
  + [ ] Added 2FA Module System
+ Added Authenticator 2FA
  + Works with Google Authenticator
  + Asks for verification when logging in
+ Added SMS 2FA (Todo)
  + [ ] Implemented SMS 2FA
  + ...
+ Added Discord Login / Register
+ Added Enable / Disable for Google, Discord and Email
+ Added hCaptcha Tab
+ Added Github Login
  + Add Enable / Disable
+ Changed Discord Login/Register Enc PW to ID (instead of email)
+ Added Facebook Login
  + Added Enable / Disable (TODO)
  + Added Setup Guide (TODO)

## Products
+ Added Product importing from Payment Providers
  + Show Products
  + Import Products (Todo)

## Mail
+ Added SMTP Settings
+ Added Mail Sending

## Stripe
+ Stripe adds Customer ID to user config

# Files Util
+ Added `updateJSONargs(file, arg, content)` function

# Other
+ Join our [Discord](https://loona.cc)!
