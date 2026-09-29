"""Read only fields explicitly present in a saved Stedi test response.

This is a narrow sandbox adapter, not a general dental benefit verification
engine. In particular, medical deductibles must not be presented as dental.
"""

def parse_stedi_response(data: dict) -> dict:
    if not isinstance(data, dict):
        raise TypeError("Eligibility response must be an object")

    def obj(value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise TypeError("Unexpected eligibility response shape")
        return value

    payer = obj(data.get("payer"))
    subscriber = obj(data.get("subscriber"))
    person = obj(obj(subscriber.get("name")).get("person"))
    payer_name = obj(payer.get("name")).get("organization") or "Not returned by eligibility source"
    subscriber_name = " ".join(
        str(part) for part in (person.get("firstName"), person.get("lastName"))
        if part
    ) or "Not returned by eligibility source"

    errors = []
    for error in data.get("errors") or []:
        if isinstance(error, dict):
            errors.append(str(error.get("description") or error.get("message") or "Unspecified source error"))
        else:
            errors.append(str(error))

    dental = []
    seen = set()

    def walk(node):
        if isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, dict):
            for item in node.get("nonCovered") or []:
                if not isinstance(item, dict):
                    continue
                service = item.get("service") or {}
                if not isinstance(service, dict):
                    continue
                name = str(service.get("definition") or "")
                if str(service.get("value") or "") != "35" and "dental" not in name.lower():
                    continue
                network = item.get("network") or {}
                messages = item.get("messages") or []
                if not isinstance(messages, list):
                    messages = [messages]
                record = {
                    "service": name or "Dental Care",
                    "status": "NON_COVERED",
                    "network": network.get("indicator") if isinstance(network, dict) else None,
                    "messages": [str(message) for message in messages],
                }
                record["network"] = record["network"] or "Not returned by eligibility source"
                key = (record["service"], record["network"], tuple(record["messages"]))
                if key not in seen:
                    dental.append(record)
                    seen.add(key)
            for child in node.values():
                walk(child)

    if not errors:
        walk(data)

    return {
        "payer": payer_name,
        "subscriber_name": subscriber_name,
        "member_id": subscriber.get("memberId") or "Not returned by eligibility source",
        "errors": errors,
        "dental": dental,
    }
