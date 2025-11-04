# import frappe

# def after_insert(doc, method):
#     message = f"[Mahakaal] New issue created: {doc.name} --from HOOKS"
#     print(message)  # shows in `bench start` terminal
#     frappe.logger().info(message)  # logs to logs/frappe.log

# def on_update(doc, method):
#     message = f"[Mahakaal] Issue updated: {doc.name}, status={doc.status} --from HOOKS"
#     print(message)
#     frappe.logger().info(message)
