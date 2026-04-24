-- offence_penalty_updates.sql
-- SQL update statements to normalise offence penalty text to match
-- Computer Misuse and Cybercrimes Act (Kenya) consolidated text.
-- Review SELECT previews before running. Make a backup first (mysqldump).

-- Section 14
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%14%' OR title LIKE '%Unauthorised access%' OR title LIKE '%Unauthorized Access%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 5,000,000 or imprisonment for a term not exceeding 3 years, or both.'
WHERE section_number LIKE '%14%' OR title LIKE '%Unauthorised access%' OR title LIKE '%Unauthorized Access%';
COMMIT;

-- Section 15
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%15%' OR title LIKE '%Access with intent%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 10,000,000 or imprisonment for a term not exceeding 10 years, or both.'
WHERE section_number LIKE '%15%' OR title LIKE '%Access with intent%';
COMMIT;

-- Section 16
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%16%' OR title LIKE '%Unauthorised interference%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 10,000,000 or imprisonment for a term not exceeding 5 years, or both. Aggravated (if resulting in significant financial loss, threatens national security, causes physical injury or death, or threatens public health or safety): fine not exceeding KES 20,000,000 or imprisonment for a term not exceeding 10 years, or both.'
WHERE section_number LIKE '%16%' OR title LIKE '%Unauthorised interference%';
COMMIT;

-- Section 17
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%17%' OR title LIKE '%Unauthorised interception%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 10,000,000 or imprisonment for a term not exceeding 5 years, or both. Aggravated (significant loss/threat to national security/physical or psychological injury or death/threat to public health or safety): fine not exceeding KES 20,000,000 or imprisonment for a term not exceeding 10 years, or both.'
WHERE section_number LIKE '%17%' OR title LIKE '%Unauthorised interception%';
COMMIT;

-- Section 18 (manufacture/supply)
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE (section_number LIKE '%18%' AND (title LIKE '%manufactur%' OR title LIKE '%supply%' OR title LIKE '%offer%' OR title LIKE '%import%' OR title LIKE '%distribut%' OR title LIKE '%make available%')) OR title LIKE '%Illegal devices%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 20,000,000 or imprisonment for a term not exceeding 10 years, or both.'
WHERE (section_number LIKE '%18%' AND (title LIKE '%manufactur%' OR title LIKE '%supply%' OR title LIKE '%offer%' OR title LIKE '%import%' OR title LIKE '%distribut%' OR title LIKE '%make available%')) OR title LIKE '%Illegal devices%';
COMMIT;

-- Section 18 (possession)
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%18%' AND (title LIKE '%possession%' OR title LIKE '%receiv%' OR title LIKE '%in possession%');
UPDATE offences
SET penalty = 'Fine not exceeding KES 10,000,000 or imprisonment for a term not exceeding 5 years, or both.'
WHERE section_number LIKE '%18%' AND (title LIKE '%possession%' OR title LIKE '%receiv%' OR title LIKE '%in possession%');
COMMIT;

-- Section 19
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%19%' OR title LIKE '%disclos%password%' OR title LIKE '%access code%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 5,000,000 or imprisonment for a term not exceeding 3 years, or both. Aggravated (if for wrongful gain/for unlawful purpose/to occasion loss): fine not exceeding KES 10,000,000 or imprisonment for a term not exceeding 5 years, or both.'
WHERE section_number LIKE '%19%' OR title LIKE '%disclos%password%' OR title LIKE '%access code%';
COMMIT;

-- Section 20
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%20%' OR title LIKE '%protected computer%' OR title LIKE '%Enhanced penalty%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 25,000,000 or imprisonment for a term not exceeding 20 years, or both.'
WHERE section_number LIKE '%20%' OR title LIKE '%protected computer%' OR title LIKE '%Enhanced penalty%';
COMMIT;

-- Section 21
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%21%' OR title LIKE '%espionag%';
UPDATE offences
SET penalty = 'Imprisonment for a period not exceeding 20 years or a fine not exceeding KES 10,000,000, or both. If the offence causes death, imprisonment for life.'
WHERE section_number LIKE '%21%' OR title LIKE '%espionag%';
COMMIT;

-- Section 22
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%22%' OR title LIKE '%False publications%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 5,000,000 or imprisonment for a term not exceeding 2 years, or both.'
WHERE section_number LIKE '%22%' OR title LIKE '%False publications%';
COMMIT;

-- Section 26
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%26%' OR title LIKE '%Computer fraud%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 20,000,000 or imprisonment for a term not exceeding 10 years, or both.'
WHERE section_number LIKE '%26%' OR title LIKE '%Computer fraud%';
COMMIT;

-- Section 31
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%31%' OR title LIKE '%Interception of electronic messages%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 200,000 or imprisonment for a term not exceeding 7 years, or both.'
WHERE section_number LIKE '%31%' OR title LIKE '%Interception of electronic messages%';
COMMIT;

-- Section 32
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%32%' OR title LIKE '%Willful misdirection%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 100,000 or imprisonment for a term not exceeding 2 years, or both.'
WHERE section_number LIKE '%32%' OR title LIKE '%Willful misdirection%';
COMMIT;

-- Section 33
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%33%' OR title LIKE '%Cyber terrorism%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 5,000,000 or imprisonment for a term not exceeding 10 years, or both.'
WHERE section_number LIKE '%33%' OR title LIKE '%Cyber terrorism%';
COMMIT;

-- Section 37
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%37%' OR title LIKE '%Wrongful distribution%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 200,000 or imprisonment for a term not exceeding 2 years, or both.'
WHERE section_number LIKE '%37%' OR title LIKE '%Wrongful distribution%';
COMMIT;

-- Section 38
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%38%' OR title LIKE '%Fraudulent use of electronic data%';
UPDATE offences
SET penalty = 'Fine not exceeding KES 200,000 or imprisonment for a term not exceeding 2 years, or both.'
WHERE section_number LIKE '%38%' OR title LIKE '%Fraudulent use of electronic data%';
COMMIT;

-- Section 46
START TRANSACTION;
-- Preview: SELECT id, title, section_number, penalty FROM offences WHERE section_number LIKE '%46%' OR title LIKE '%Additional penalty%';
UPDATE offences
SET penalty = 'Penalty similar to the penalty provided under the underlying law; the court shall consider the manner in which the use of a computer system enhanced the impact of the offence, whether the offence resulted in a commercial advantage or financial gain, the value involved, breach of trust, the number of victims, the conduct of the accused, and any other matter the court deems fit.'
WHERE section_number LIKE '%46%' OR title LIKE '%Additional penalty%';
COMMIT;
