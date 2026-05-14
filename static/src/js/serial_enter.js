/** @odoo-module **/

console.log("✅ Serial Enter JS Loaded");

// 🔥 MUST use capture = true
window.addEventListener("keydown", function (ev) {

    if (ev.key !== "Enter") return;

    const active = document.activeElement;

    if (!active) return;

    if (active.tagName !== "INPUT") return;

    // 🔥 DEBUG
    console.log("ENTER pressed on:", active);

    // 🔥 Check correct field
    const fieldWidget = active.closest(".o_field_widget");

    if (!fieldWidget) {
        console.log("❌ Not inside field widget");
        return;
    }

    const fieldName = fieldWidget.getAttribute("name");

    console.log("Field Name:", fieldName);

    if (fieldName !== "serial_input") {
        console.log("❌ Not serial_input");
        return;
    }

    ev.preventDefault();
    ev.stopPropagation();

    // 🔥 find row
    const row = active.closest("tr");
    if (!row) {
        console.log("❌ Row not found");
        return;
    }

    // 🔥 find scan button
    const btn = row.querySelector("button[name='action_scan_serial']");

    if (btn) {
        console.log("🚀 ENTER → Scan triggered");
        btn.click();
    } else {
        console.log("❌ Scan button missing");
    }

}, true); // 🔥 THIS IS IMPORTANT