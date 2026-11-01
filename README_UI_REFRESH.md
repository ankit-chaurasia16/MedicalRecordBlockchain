# MedicalChain — Professional UI Refresh

This is a **visual-only patch** for the existing multi-role MedicalChain project.

## Included files
- `templates/base.html` — refreshed application shell, sidebar, header, and public page layout.
- `templates/login.html` — redesigned sign-in page with links to all six registration flows and administrator login.
- `static/style.css` — responsive visual system for navigation, cards, dashboards, tables, forms, alerts, and authentication pages.

## Install on Windows
1. Stop the Flask server by pressing `Ctrl + C` in the terminal where it is running.
2. Extract this ZIP directly into `C:\Users\ankit\MedicalRecordBlockchain`.
3. The ZIP already contains the `templates` and `static` folders at its root. Allow Windows to replace **only** `templates\base.html`, `templates\login.html`, and `static\style.css`.
4. Start Flask using your existing command:

```powershell
python -c "import app; app.app.config['TEMPLATES_AUTO_RELOAD']=True; app.app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)"
```

5. Open `http://127.0.0.1:5001/login` and press `Ctrl + F5` for a hard refresh.

## Safety
- No database migration is included or required.
- No Flask routes, Python logic, SQL, form field names, account permissions, approval rules, or blockchain files are changed.
- This is an academic demonstration. Use fictional patient data only.
