#!/usr/bin/env python3
"""
update_offence_penalties.py

Preview and apply penalty text corrections to the `offences` table in the
local MySQL database used by the Legal Awareness System.

Usage:
  - Edit DB credentials at the top, or set environment variables DB_HOST, DB_USER,
    DB_PASS, DB_NAME. If DB_PASS is not set the script will prompt for it.
  - Run: python update_offence_penalties.py

The script will:
  1. Show DISTINCT section_number values found in the table (helpful to craft
     more precise matches if necessary).
  2. For each statutory section this project tracks, preview rows that match
     the WHERE clause and show current penalty values.
  3. Ask for confirmation before applying all updates inside transactions.
  4. Apply updates and print a summary.

This is a local-only script. Make a backup (mysqldump) before running.
"""
import os
import sys
from getpass import getpass
import mysql.connector

# -- Configuration (override with environment variables if desired) --
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS')  # if None, will prompt
DB_NAME = os.getenv('DB_NAME', 'legal_awareness_db')

if not DB_PASS:
    DB_PASS = getpass('MySQL password for user %s: ' % DB_USER)

try:
    conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
except mysql.connector.Error as e:
    print('Error connecting to MySQL:', e)
    sys.exit(1)

cur = conn.cursor(dictionary=True)

def show_distinct_sections():
    cur.execute('SELECT DISTINCT section_number FROM offences ORDER BY section_number')
    rows = cur.fetchall()
    print('\nFound section_number values (sample):')
    for r in rows[:200]:
        print(' -', r['section_number'])

updates = [
    {
        'desc': 'Section 14 — Unauthorised access',
        'where': "section_number LIKE '%14%' OR title LIKE '%Unauthoris%Access%' OR title LIKE '%Unauthorized Access%'",
        'text': 'Fine not exceeding KES 5,000,000 or imprisonment for a term not exceeding 3 years, or both.'
    },
    {
        'desc': 'Section 15 — Access with intent to commit further offence',
        'where': "section_number LIKE '%15%' OR title LIKE '%Access with intent%'",
        'text': 'Fine not exceeding KES 10,000,000 or imprisonment for a term not exceeding 10 years, or both.'
    },
    {
        'desc': 'Section 16 — Unauthorised interference (includes aggravated)',
        'where': "section_number LIKE '%16%' OR title LIKE '%Unauthorised interference%'",
        'text': 'Fine not exceeding KES 10,000,000 or imprisonment for a term not exceeding 5 years, or both. Aggravated (if resulting in significant financial loss, threatens national security, causes physical injury or death, or threatens public health or safety): fine not exceeding KES 20,000,000 or imprisonment for a term not exceeding 10 years, or both.'
    },
    {
        'desc': 'Section 17 — Unauthorised interception (includes aggravated)',
        'where': "section_number LIKE '%17%' OR title LIKE '%Unauthorised interception%'",
        'text': 'Fine not exceeding KES 10,000,000 or imprisonment for a term not exceeding 5 years, or both. Aggravated (significant loss/threat to national security/physical or psychological injury or death/threat to public health or safety): fine not exceeding KES 20,000,000 or imprisonment for a term not exceeding 10 years, or both.'
    },
    {
        'desc': 'Section 18 — Illegal devices and access codes (manufacture/supply)',
        'where': "(section_number LIKE '%18%' AND (title LIKE '%manufactur%' OR title LIKE '%supply%' OR title LIKE '%offer%' OR title LIKE '%import%' OR title LIKE '%distribut%' OR title LIKE '%make available%')) OR title LIKE '%Illegal devices%'",
        'text': 'Fine not exceeding KES 20,000,000 or imprisonment for a term not exceeding 10 years, or both.'
    },
    {
        'desc': 'Section 18 — Illegal devices and access codes (possession/receiving)',
        'where': "section_number LIKE '%18%' AND (title LIKE '%possession%' OR title LIKE '%receiv%' OR title LIKE '%in possession%')",
        'text': 'Fine not exceeding KES 10,000,000 or imprisonment for a term not exceeding 5 years, or both.'
    },
    {
        'desc': 'Section 19 — Unauthorised disclosure of password or access code',
        'where': "section_number LIKE '%19%' OR title LIKE '%disclos%password%' OR title LIKE '%access code%'",
        'text': 'Fine not exceeding KES 5,000,000 or imprisonment for a term not exceeding 3 years, or both. Aggravated (if for wrongful gain/for unlawful purpose/to occasion loss): fine not exceeding KES 10,000,000 or imprisonment for a term not exceeding 5 years, or both.'
    },
    {
        'desc': 'Section 20 — Enhanced penalty for offences involving protected computer system',
        'where': "section_number LIKE '%20%' OR title LIKE '%protected computer%' OR title LIKE '%Enhanced penalty%'",
        'text': 'Fine not exceeding KES 25,000,000 or imprisonment for a term not exceeding 20 years, or both.'
    },
    {
        'desc': 'Section 21 — Cyber espionage',
        'where': "section_number LIKE '%21%' OR title LIKE '%espionag%'",
        'text': 'Imprisonment for a period not exceeding 20 years or a fine not exceeding KES 10,000,000, or both. If the offence causes death, imprisonment for life.'
    },
    {
        'desc': 'Section 22 — False publications',
        'where': "section_number LIKE '%22%' OR title LIKE '%False publications%'",
        'text': 'Fine not exceeding KES 5,000,000 or imprisonment for a term not exceeding 2 years, or both.'
    },
    {
        'desc': 'Section 26 — Computer fraud',
        'where': "section_number LIKE '%26%' OR title LIKE '%Computer fraud%'",
        'text': 'Fine not exceeding KES 20,000,000 or imprisonment for a term not exceeding 10 years, or both.'
    },
    {
        'desc': 'Section 31 — Interception of electronic messages or money transfers',
        'where': "section_number LIKE '%31%' OR title LIKE '%Interception of electronic messages%'",
        'text': 'Fine not exceeding KES 200,000 or imprisonment for a term not exceeding 7 years, or both.'
    },
    {
        'desc': 'Section 32 — Willful misdirection of electronic messages',
        'where': "section_number LIKE '%32%' OR title LIKE '%Willful misdirection%'",
        'text': 'Fine not exceeding KES 100,000 or imprisonment for a term not exceeding 2 years, or both.'
    },
    {
        'desc': 'Section 33 — Cyber terrorism',
        'where': "section_number LIKE '%33%' OR title LIKE '%Cyber terrorism%'",
        'text': 'Fine not exceeding KES 5,000,000 or imprisonment for a term not exceeding 10 years, or both.'
    },
    {
        'desc': 'Section 37 — Wrongful distribution of obscene or intimate images',
        'where': "section_number LIKE '%37%' OR title LIKE '%Wrongful distribution%'",
        'text': 'Fine not exceeding KES 200,000 or imprisonment for a term not exceeding 2 years, or both.'
    },
    {
        'desc': 'Section 38 — Fraudulent use of electronic data',
        'where': "section_number LIKE '%38%' OR title LIKE '%Fraudulent use of electronic data%'",
        'text': 'Fine not exceeding KES 200,000 or imprisonment for a term not exceeding 2 years, or both.'
    },
    {
        'desc': 'Section 46 — Additional penalty for other offences committed through use of a computer system',
        'where': "section_number LIKE '%46%' OR title LIKE '%Additional penalty%'",
        'text': 'Penalty similar to the penalty provided under the underlying law; the court shall consider the manner in which the use of a computer system enhanced the impact of the offence, whether the offence resulted in a commercial advantage or financial gain, the value involved, breach of trust, the number of victims, the conduct of the accused, and any other matter the court deems fit.'
    }
]

def preview_update(u):
    q = f"SELECT id, title, section_number, penalty FROM offences WHERE {u['where']}"
    cur.execute(q)
    rows = cur.fetchall()
    print('\n==', u['desc'], '==')
    print('Matched rows:', len(rows))
    for r in rows:
        print(f"  id={r['id']} | section_number={r['section_number']} | title={r['title']}\n    current penalty: {r['penalty']}")
    return rows

def apply_update(u):
    # use a simple UPDATE with the new text
    update_sql = f"UPDATE offences SET penalty = %s WHERE {u['where']}"
    cur.execute('START TRANSACTION')
    cur.execute(update_sql, (u['text'],))
    affected = cur.rowcount
    cur.execute('COMMIT')
    return affected

def main():
    print('Connected to', DB_NAME, 'on', DB_HOST)
    show_distinct_sections()

    total_matches = 0
    per_update_matches = []
    for u in updates:
        rows = preview_update(u)
        per_update_matches.append((u['desc'], len(rows)))
        total_matches += len(rows)

    print('\nSummary:')
    for desc, cnt in per_update_matches:
        print(f' - {desc}: {cnt} row(s) matched')

    if total_matches == 0:
        print('\nNo rows matched the preview filters. Aborting.')
        cur.close()
        conn.close()
        return

    confirm = input('\nApply all updates above? Type YES to proceed: ')
    if confirm != 'YES':
        print('Aborted — no changes made.')
        cur.close()
        conn.close()
        return

    print('\nApplying updates...')
    summary = []
    for u in updates:
        affected = apply_update(u)
        summary.append((u['desc'], affected))
        print(f"Updated: {u['desc']} — {affected} row(s) affected")

    print('\nDone. Summary:')
    for desc, affected in summary:
        print(f' - {desc}: {affected} row(s) updated')

    # Write SQL file for record / manual run
    sql_path = os.path.join(os.path.dirname(__file__), 'sql', 'offence_penalty_updates.sql')
    try:
        os.makedirs(os.path.dirname(sql_path), exist_ok=True)
        with open(sql_path, 'w', encoding='utf-8') as f:
            for u in updates:
                f.write('-- ' + u['desc'] + '\n')
                f.write('START TRANSACTION;\n')
                f.write("-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE %s;\n" % u['where'])
                f.write("UPDATE offences SET penalty = '%s' WHERE %s;\n" % (u['text'].replace("'", "''"), u['where']))
                f.write('COMMIT;\n\n')
        print('Wrote SQL file to', sql_path)
    except Exception as e:
        print('Warning: could not write SQL file:', e)

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
