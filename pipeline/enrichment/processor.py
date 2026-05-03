from pipeline.warden.protector import Protector
from pipeline.warden.normalize_orthography import Warden
from pipeline.warden.agreement import AgreementEngine


class EnricherProcessor:
    def __init__(self, db_path: str = 'data/pems_core.db'):
        self.protector = Protector(db_path=db_path)
        self.warden = Warden(db_path=db_path)
        self.engine = AgreementEngine(db_path=db_path)

    def process(self, text: str) -> str:
        # Mask exceptions
        masked, imm_map = self.protector.protect(text)
        # Normalize orthography (apply mappings) while exceptions are masked
        mapped = self.warden.apply_mappings(masked)
        # Restore exceptions now so AgreementEngine sees the real noun positions
        restored = self.protector.restore(mapped, imm_map)
        # Apply agreement rules (possessive + adjective) on restored text
        agreed = self.engine.apply_all_agreement(restored)
        return agreed
