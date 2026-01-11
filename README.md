Custom TCP Packet Generator & Chat Application
פרויקט זה מדגים את תהליך ה-Encapsulation (אריזה) של נתונים במודל ה-TCP/IP, החל מיצירת פקטות "ידנית" מקובץ CSV ועד לבניית אפליקציית צ'אט מלאה (Client-Server) עם ממשק גרפי.
🚀 תכונות עיקריות
יצירת פקטות מותאמות אישית: אריזת נתונים גולמיים לתוך כותרות TCP ו-IP באופן תוכנתי.

אפליקציית צ'אט (GUI): ממשק משתמש ב-Tkinter המאפשר התחברות לשרת, צפייה ברשימת משתמשים וניהול שיחות בזמן אמת.

שרת מרובה משתתפים (Multi-threaded): שרת המסוגל לנהל מספר חיבורים בו-זמנית ולנתב הודעות בין לקוחות.

ניתוח תעבורה: אימות מלא של שליחת הנתונים באמצעות Wireshark.
טכנולוגיות
Python (Socket programming, Threading, Tkinter)

Wireshark (Network Analysis)

Scapy (לשלב בניית הפקטות)

מבנה הפרויקטserver.py: שרת ה-TCP המנהל את הלוגיקה של הצ'אט.guiclient.py: לקוח הצ'אט עם ממשק המשתמש הגרפי.packets_data.csv: בסיס הנתונים הגולמי ליצירת הפקטות בשלב א'.📊 ניתוח רשת (Wireshark)במהלך הפרויקט בוצע ניתוח מעמיק של שכבות הרשת:Application Layer: שליחת פקודות כמו NAME ו-MSG.Transport Layer (TCP): ניתוח של ה-Three-way Handshake (SYN, SYN-ACK, ACK) ושימוש בפורט 10000.Network Layer (IP): שימוש בכתובות IPv4 פנימיות וכתובת Loopback ($127.0.0.1$).
הוראות הרצה
הפעל את השרת:


python server.py
הפעל את הלקוח (ניתן לפתוח מספר חלונות כדי לדמות צ'אט בין משתמשים):


python guiclient.py
