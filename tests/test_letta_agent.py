import unittest
from types import SimpleNamespace

from hannario.letta_agent import extract_tool_events, looks_like_private_control_json


class LettaAgentTest(unittest.TestCase):
    def test_looks_like_private_control_json(self) -> None:
        self.assertTrue(
            looks_like_private_control_json(
                '{"action":"none","reason":"なし","channel_id":null,"message":""}'
            )
        )
        self.assertFalse(looks_like_private_control_json('{"ok": true}'))
        self.assertFalse(looks_like_private_control_json("普通の返答"))

    def test_extract_tool_events(self) -> None:
        response = SimpleNamespace(
            messages=[
                SimpleNamespace(
                    message_type="tool_call_message",
                    tool_calls=[
                        {
                            "name": "list_observed_discord_channels",
                            "arguments": "{}",
                        }
                    ],
                ),
                SimpleNamespace(
                    message_type="tool_return_message",
                    name="list_observed_discord_channels",
                    status="success",
                    tool_return="#general: 1 observations",
                ),
            ]
        )

        events = extract_tool_events(response)

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].kind, "call")
        self.assertEqual(events[0].name, "list_observed_discord_channels")
        self.assertEqual(events[0].arguments, "{}")
        self.assertEqual(events[1].kind, "return")
        self.assertEqual(events[1].status, "success")
        self.assertEqual(events[1].text, "#general: 1 observations")


if __name__ == "__main__":
    unittest.main()
