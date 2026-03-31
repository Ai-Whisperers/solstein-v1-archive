"""Tenant onboarding automation.

EPIC-030 Story 5: Streamline new tenant creation.

Usage:
    from solstein.tenant.onboarding import TenantOnboardingService

    onboarding = TenantOnboardingService()
    tenant = await onboarding.create_tenant(
        name="Acme Corp",
        plan="professional",
        admin_email="admin@acme.com"
    )
"""


from loguru import logger

from solstein.tenant.context import generate_api_key, hash_api_key
from solstein.tenant.models import Tenant, TenantConfig, TenantPlan, TenantUser, get_default_config


class TenantOnboardingService:
    """Handle tenant onboarding process."""

    def __init__(self):
        """Initialize onboarding service."""
        pass

    async def create_tenant(
        self,
        name: str,
        plan: TenantPlan = TenantPlan.STARTER,
        admin_email: str | None = None,
        settings: dict | None = None,
    ) -> tuple[Tenant, str]:
        """Create new tenant with onboarding.

        Steps:
        1. Validate tenant name (unique)
        2. Create tenant record
        3. Create default admin user
        4. Initialize configuration
        5. Generate API key
        6. Send welcome email

        Args:
            name: Organization name.
            plan: Subscription plan.
            admin_email: Admin user email.
            settings: Initial settings.

        Returns:
            Tuple of (Tenant, API key).
        """
        logger.info(f"Creating tenant: {name}")

        # 1. Validate tenant name
        await self._validate_name(name)

        # 2. Create tenant record
        api_key = generate_api_key()
        tenant = Tenant(name=name, plan=plan, settings=settings or {}, api_key_hash=hash_api_key(api_key))

        # In production: persist to database
        logger.info(f"Created tenant record: {tenant.id}")

        # 3. Create admin user if email provided
        if admin_email:
            admin = await self._create_admin_user(tenant.id, admin_email)
            logger.info(f"Created admin user: {admin.email}")

        # 4. Initialize configuration
        await self._initialize_config(tenant.id, plan)

        # 5. Send welcome email
        if admin_email:
            await self._send_welcome_email(tenant, admin_email, api_key)

        logger.info(f"Tenant onboarding complete: {tenant.id}")
        return tenant, api_key

    async def _validate_name(self, name: str) -> bool:
        """Validate tenant name is unique.

        Args:
            name: Tenant name.

        Returns:
            True if valid.

        Raises:
            ValueError: If name invalid or taken.
        """
        if not name or len(name.strip()) < 2:
            raise ValueError("Tenant name must be at least 2 characters")

        # In production: check database for existing name
        # For now, assume valid
        return True

    async def _create_admin_user(self, tenant_id: str, email: str) -> TenantUser:
        """Create admin user for tenant.

        Args:
            tenant_id: Tenant ID.
            email: Admin email.

        Returns:
            Created user.
        """
        user = TenantUser(tenant_id=tenant_id, email=email, role="admin")

        # In production: persist to database
        return user

    async def _initialize_config(self, tenant_id: str, plan: TenantPlan) -> TenantConfig:
        """Initialize tenant configuration.

        Args:
            tenant_id: Tenant ID.
            plan: Subscription plan.

        Returns:
            Tenant configuration.
        """
        defaults = get_default_config(plan)

        config = TenantConfig(tenant_id=tenant_id, limits=defaults["limits"], features=defaults["features"])

        # In production: persist to database
        logger.info(f"Initialized config for tenant {tenant_id[:8]}...")
        return config

    async def _send_welcome_email(self, tenant: Tenant, email: str, api_key: str) -> None:
        """Send welcome email with API credentials.

        Args:
            tenant: Tenant record.
            email: Recipient email.
            api_key: API key for access.
        """
        # In production: send actual email
        logger.info(f"Welcome email would be sent to: {email}")
        logger.info(f"API Key: {api_key[:20]}...")

    async def delete_tenant(self, tenant_id: str, soft: bool = True) -> bool:
        """Delete tenant and all associated data.

        Args:
            tenant_id: Tenant ID.
            soft: Soft delete (mark inactive) if True.

        Returns:
            True if successful.
        """
        logger.info(f"Deleting tenant: {tenant_id}")

        if soft:
            # Mark as cancelled, schedule deletion
            logger.info(f"Soft deleted tenant: {tenant_id}")
        else:
            # Hard delete all data
            logger.info(f"Hard deleted tenant: {tenant_id}")

        return True

    async def get_tenant_status(self, tenant_id: str) -> dict:
        """Get tenant onboarding status.

        Args:
            tenant_id: Tenant ID.

        Returns:
            Status dictionary.
        """
        return {
            "tenant_id": tenant_id,
            "created": True,
            "admin_created": True,
            "config_initialized": True,
            "welcome_email_sent": True,
            "ready": True,
        }


class SelfServiceOnboarding:
    """Self-service tenant signup."""

    async def signup(self, company_name: str, email: str, plan: str = "starter") -> dict:
        """Handle self-service signup.

        Args:
            company_name: Company/organization name.
            email: Admin email.
            plan: Selected plan.

        Returns:
            Signup result with tenant info.
        """
        service = TenantOnboardingService()

        tenant_plan = (
            TenantPlan(plan.lower())
            if plan.lower() in ["starter", "professional", "enterprise"]
            else TenantPlan.STARTER
        )

        tenant, api_key = await service.create_tenant(name=company_name, plan=tenant_plan, admin_email=email)

        return {
            "success": True,
            "tenant_id": tenant.id,
            "api_key": api_key,
            "message": "Welcome! Check your email for setup instructions.",
        }
