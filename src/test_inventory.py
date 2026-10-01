import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('inventory', Path(__file__).with_name('inventory.py'))
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def test_empty_inventory_is_real_zero(self):
        with patch.object(inventory, 'fetch', return_value={'models': []}):
            lines = inventory.collect()
        self.assertIn('ollama_inventory_models 0', lines)
        self.assertIn('ollama_inventory_loaded_models 0', lines)
        self.assertIn('ollama_inventory_loaded_vram_bytes 0', lines)

    def test_failure_replaces_previous_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'ollama.prom'
            output.write_text('ollama_inventory_models 99\n')
            with patch.object(inventory, 'OUTPUT', output), patch.object(
                    inventory, 'fetch', side_effect=TimeoutError):
                inventory.main()
            text = output.read_text()
            self.assertIn('ollama_inventory_up 0', text)
            self.assertNotIn('ollama_inventory_models', text)
            self.assertFalse(output.with_suffix('.prom.tmp').exists())

    def test_invalid_sizes_are_not_zero_filled(self):
        for value in [None, True, -1, float('nan'), float('inf'), '12']:
            with self.assertRaises(ValueError):
                inventory.nonnegative(value)

    def test_labels_are_escaped(self):
        self.assertEqual(inventory.label('a"b\\c\nd'), 'a\\"b\\\\c\\nd')


if __name__ == '__main__':
    unittest.main()
