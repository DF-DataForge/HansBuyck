import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Configure the installation service for Sales Planning.

    Done in Python (not XML) so that a renamed field in a future Enterprise
    version only logs a warning instead of blocking the installation.
    """
    slot_fields = env["planning.slot"]._fields
    _logger.info(
        "hansbuyck_workflow_planning: planning.slot relational/date fields: %s",
        sorted(name for name, f in slot_fields.items() if f.type in ("many2one", "many2many", "datetime", "date")),
    )
    product = env.ref("hansbuyck_workflow.product_plaatsing", raise_if_not_found=False)
    role = env.ref("hansbuyck_workflow_planning.planning_role_plaatser", raise_if_not_found=False)
    if not product:
        return
    fields = product._fields
    vals = {}
    day = env.ref("uom.product_uom_day", raise_if_not_found=False)
    if day and "uom_id" in fields:
        vals["uom_id"] = day.id
    if "planning_enabled" in fields:
        vals["planning_enabled"] = True
    else:
        _logger.warning("hansbuyck_workflow_planning: field product.template.planning_enabled not found")
    if role and "planning_role_id" in fields:
        vals["planning_role_id"] = role.id
    else:
        _logger.warning("hansbuyck_workflow_planning: field product.template.planning_role_id not found")
    try:
        with env.cr.savepoint():
            product.write(vals)
        _logger.info("hansbuyck_workflow_planning: configured %s with %s", product.name, list(vals))
    except Exception:
        _logger.exception("hansbuyck_workflow_planning: could not configure %s", product.name)
