from extras.scripts import Script
from dcim.models import MACAddress
import requests

class OmniVistaImportScript(Script):
    class Meta:
        name = "OmniVista MAC Import"

    def run(self, data, commit):
        token = "xxxxxx"
        omnivista_url = "https://10.120.0.11"
        username = "xxxx"
        password = "xxxx"

        # Login
        self.log_info("🔐 Melde mich bei OmniVista an...")
        session = requests.Session()
        login_response = session.post(
            f"{omnivista_url}/rest-api/login",
            json={"userName": username, "password": password},
            verify=False
        )
        if login_response.status_code != 200:
            self.log_failure("❌ Login fehlgeschlagen")
            return
        access_token = login_response.json().get("accessToken")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json;charset=UTF-8"
        }

        # Hole alle MACs
        for mac in MACAddress.objects.all():
            clean_mac = mac.mac_address.replace(":", "").upper()
            arp = mac.custom_field_data.get("ARP", [])
            if not arp:
                self.log_info(f"⚠️ MAC {clean_mac} hat kein ARP-Feld")
                continue
            arp_value = arp[0]

            body = {
                "username": clean_mac,
                "password": clean_mac,
                "repeat": clean_mac,
                "telephone": "1234567890",
                "email": f"{clean_mac}@autogen.4net.ch",
                "fullName": f"Device {clean_mac}",
                "department": "BBA",
                "position": "AutoImported",
                "description": "MAC Import from NetBox",
                "accessRoleProfile": arp_value,
                "otherAttributesVOs": []
            }

            self.log_info(f"👤 Erstelle Benutzer {clean_mac} mit ARP: {arp_value}")
            response = session.post(
                f"{omnivista_url}/api/ham/userAccount/addUser",
                json=body,
                headers=headers,
                verify=False
            )
            if response.status_code == 200:
                self.log_success(f"✅ Benutzer {clean_mac} erfolgreich erstellt.")
            else:
                self.log_failure(f"❌ Fehler bei {clean_mac}: {response.status_code} → {response.text}")
