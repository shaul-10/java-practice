# הוראות לקלוד — בניית תרגילי כתיבה (סוג ב׳) לפרק חדש

## הקשר

אתה עוזר לבנות תרגילי כתיבת קוד Java לקורס מבוא למדעי המחשב.
תרגילים אלה הם **סוג ב׳** — הסטודנט מוריד קובץ Java, משלים שיטה, ומריץ בודקים.
הם נייבאים ל-Moodle כ-XML.

---

## מה כבר קיים בפרויקט זה

- **פרק 6.1** (מערכים חד ממדיים) — 10 תרגילי כתיבה מוכנים ב-`Arrays1d_All_Questions.xml`
- **שאלות סגורות** — קיימים קבצי JSON לרמות 01, 02, 03

---

## המשימה הנוכחית

בניית תרגילי כתיבה לפרק **6.2 — פעולות על מערכים חד ממדיים**.

---

## שלב 1 — הצע רשימת תרגילים

לפני שבונים כלום — הצג טבלה עם עמודות:

| # | שם השיטה | תיאור קצר | רמה | סוג החזרה |
|---|----------|-----------|-----|-----------|

### כללים לבחירת תרגילים
- **אל תקח** תרגילים כפי שהם מהשקפים — אלה נפתרו בכיתה
- **אל תקח** תרגילים ישירות מ-CodingBat — השתמש רק כהשראה
- צור תרגילים **מקוריים** ברמת קושי דומה
- התחל מרמה בסיסית ועלה בהדרגה
- כל התרגילים קשורים לנושא הפרק הנוכחי

### קשת הרמות המומלצת ל-10 תרגילים
| תרגילים | רמה |
|---------|-----|
| 1–3 | ⭐ בסיסי |
| 4–7 | ⭐⭐ ביניים |
| 8–10 | ⭐⭐⭐ מתקדם |

---

## שלב 2 — לאחר אישור הרשימה

בנה קובץ XML אחד המכיל את כל התרגילים.

### מוסכמת שמות

**קובץ XML:**
```
[UnitKeyword]_All_Questions.xml

דוגמה לפרק 6.2:
  Arrays1dOps_All_Questions.xml
```

**קבצי Java בתוך ה-XML:**
```
Arrays##_MethodName.java
(## = 01, 02, ..., 10)
```

---

## פורמט קובץ Java — תבנית מחייבת

```java
/**
 * Exercise: 1D Arrays – [Description]
 *
 * Write a static method:
 *   public static RETURN_TYPE methodName(PARAMS)
 *
 * [תיאור המשימה — באנגלית בלבד]
 *
 * Examples:
 *   methodName(...)  -->  ...
 *   methodName(...)  -->  ...
 *   methodName(...)  -->  ...
 */
public class Arrays##_MethodName {

    // ============================================================
    // Complete the method below
    // ============================================================
    public static RETURN_TYPE methodName(PARAMS) {
        // TODO: write your solution here

    }

    // ============================================================
    // Tests - do not change
    // ============================================================
    public static void main(String[] args) {

        // --- Examples from instructions ---
        System.out.println("run methodName(X)    Expected: Y    Actual: "
            + methodName(X) + "    " + (methodName(X) == Y ? "V PASS" : "X FAIL"));

        // --- Edge cases ---
        System.out.println("run methodName(X)    Expected: Y    Actual: "
            + methodName(X) + "    " + (methodName(X) == Y ? "V PASS" : "X FAIL"));
    }
}
```

### כללים קריטיים לקובץ Java
- **כל הטקסט — באנגלית בלבד** (JavaDoc, הערות, הדפסות) — אין עברית בתוך code!
- חלק TODO — **ריק לחלוטין**, אפס קוד
- לפחות **4-5 טסטים** (דוגמאות מההוראות + מקרי קצה)
- **אין `// ב-main` ואין שום טקסט עברי בקוד**

### פורמט טסטים לפי סוג המתודה

**מתודה עם ערך מוחזר (int, boolean, double...):**
```java
System.out.println("run method(X)    Expected: Y    Actual: "
    + method(X) + "    " + (method(X) == Y ? "V PASS" : "X FAIL"));
```

**מתודה void שמדפיסה:**
```java
System.out.print("Test 1 - Expected: X Y Z    Actual: ");
method(new int[]{...});
```

**מתודה void שמשנה מערך:**
```java
int[] a = {1, 2, 3};
method(a, param);
System.out.println("Expected: {X,Y,Z}    Actual: {" + a[0]+","+a[1]+","+a[2]+"}"
    + "    " + (a[0]==X && a[1]==Y && a[2]==Z ? "V PASS" : "X FAIL"));
```

**מתודה המחזירה מערך:**
```java
// helper methods - do not change:
private static String arrayToStr(int[] a) { ... }
private static boolean arrEq(int[] a, int[] b) { ... }
```

---

## פורמט XML — מבנה כל שאלה

כל שאלה ב-XML מכילה:

```xml
<question type="description">
    <name>
      <text>Q1 – arrays1d – method name</text>
    </name>
    <questiontext format="html">
      <text><![CDATA[<!-- HTML בעברית עם תיאור השאלה -->]]></text>
      <file name="Arrays01_MethodName.java" path="/" encoding="base64">BASE64_ENCODED_JAVA</file>
    </questiontext>
    <generalfeedback format="html">
      <text></text>
    </generalfeedback>
    <defaultgrade>0</defaultgrade>
    <penalty>0</penalty>
    <hidden>0</hidden>
  </question>
```

### HTML בתוך ה-XML — תבנית

```html
<h3 dir="rtl"><img src="https://www.freeiconspng.com/uploads/bluej-icon-png-0.png"
     alt="BlueJ" width="50" height="50" class="img-responsive atto_image_button_text-bottom"></h3>

<h4 dir="rtl" style="text-align: right;">שאלה N – [נושא] – [כותרת בעברית]</h4>

<p dir="rtl" style="text-align: right;">
כתבו שיטה סטטית <strong>[signature]</strong><br>
[תיאור בעברית]
</p>

<p dir="rtl" style="text-align: right;"><strong>דוגמאות ריצה:</strong></p>
<pre style="text-align: left; direction: ltr; background:#f4f4f4; padding:8px; border-radius:4px;">method(...)  →  ...
method(...)  →  ...</pre>

<p dir="rtl" style="text-align: right;">
הורידו את המחלקה <strong><a href="@@PLUGINFILE@@/Arrays##_MethodName.java"
download="Arrays##_MethodName.java" style="text-decoration: underline;">Arrays##_MethodName.java</a></strong>
לסביבת העבודה, השלימו את השיטה והריצו את הטסטים (התוכנית הראשית).
</p>
```

---

## בניית ה-XML — שיטת עבודה מומלצת

בנה את ה-XML בסקריפט Python:
1. הגדר את כל קבצי ה-Java כמחרוזות
2. עבד לכל קובץ: `base64.b64encode(src.encode("utf-8")).decode("ascii")`
3. בנה את ה-XML המלא
4. שמור לקובץ `.xml`

---

## בדיקות לפני מסירה

לאחר יצירת ה-XML, בדוק:
- [ ] אין טקסט עברי בשדות code של ה-Java
- [ ] כל מתודה מכילה לפחות 4 טסטים
- [ ] שם ה-XML תואם למוסכמה
- [ ] כל שאלה מכילה HTML בעברית + קובץ Java ב-base64
- [ ] `<file>` נמצא **בתוך** `<questiontext>` (לא אחריו)
- [ ] כל שאלה מכילה קישור `@@PLUGINFILE@@` עם `download=`
- [ ] `defaultgrade` = 0
- [ ] שורות הדוגמאות ב-`<pre>` אינן מכילות רווחים מובילים — כל שורה מתחילה מהתחלה
- [ ] `<pre>` כולל `background:#f4f4f4; padding:8px; border-radius:4px;`
- [ ] חתימת השיטה עטופה ב-`<strong>` בלבד — לא `<strong><code>`
- [ ] כותרת הדוגמאות: `דוגמאות ריצה:` (לא `דוגמאות:`)
