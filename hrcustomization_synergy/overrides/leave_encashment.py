import frappe
from frappe import _
from frappe.utils import flt
from hrms.hr.doctype.leave_encashment.leave_encashment import LeaveEncashment

class CustomLeaveEncashment(LeaveEncashment):
    def set_encashment_amount(self):
        salary_assignment_list = frappe.get_all(
            "Salary Structure Assignment",
            filters={"employee": self.employee, "from_date": ("<=", self.encashment_date)},
            order_by="from_date desc",
            limit_page_length=1
        )
        if not salary_assignment_list:
            frappe.throw(_("No Salary Structure Assignment found for Employee {0}").format(self.employee))
        salary_assignment = frappe.get_doc("Salary Structure Assignment", salary_assignment_list[0].name)
        custom_formula = frappe.db.get_value(
            "Salary Structure", salary_assignment.salary_structure, "custom_leave_salary_formula"
        )
        
        if custom_formula:
            context = salary_assignment.as_dict()
            try:
                per_day_encashment = flt(frappe.safe_eval(custom_formula, None, context))
            except Exception as e:
                frappe.throw(_("Error in evaluating leave salary formula: {0}").format(e))
        else:
            per_day_encashment = frappe.db.get_value(
                "Salary Structure", salary_assignment.salary_structure, "leave_encashment_amount_per_day"
            )
            if not per_day_encashment:
                per_day_encashment = 0
        self.encashment_amount = self.encashment_days * per_day_encashment
