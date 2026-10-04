import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Protocol
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class CustomerType(Enum):
    """Enum for customer types with extensive metadata"""
    PREMIUM = "premium"
    REGULAR = "regular"
    VIP = "vip"
    STUDENT = "student"
    
    @property
    def display_name(self) -> str:
        return self.value.title()
    
    @property
    def priority_level(self) -> int:
        priority_map = {
            'vip': 1,
            'premium': 2, 
            'regular': 3,
            'student': 4
        }
        return priority_map.get(self.value, 999)

@dataclass
class DiscountRequest:
    """Data class for discount calculation requests"""
    customer_id: str
    customer_type: CustomerType
    base_price: float
    product_category: str
    
    def __post_init__(self):
        if self.base_price < 0:
            raise ValueError("Price cannot be negative")

@dataclass  
class DiscountResult:
    """Data class for discount calculation results"""
    original_price: float
    discount_amount: float
    final_price: float
    customer_type: CustomerType
    calculation_method: str

class DiscountStrategy(ABC):
    """Abstract base class for discount calculation strategies"""
    
    @abstractmethod
    def calculate_discount(self, price: float) -> float:
        """Calculate discount amount for given price"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get human-readable strategy name"""
        pass

class PremiumDiscountStrategy(DiscountStrategy):
    """Discount strategy for premium customers"""
    
    def __init__(self, discount_rate: float = 0.15):
        self.discount_rate = discount_rate
    
    def calculate_discount(self, price: float) -> float:
        return price * self.discount_rate
    
    def get_strategy_name(self) -> str:
        return f"Premium ({self.discount_rate*100}% discount)"

class RegularDiscountStrategy(DiscountStrategy):
    """Discount strategy for regular customers"""
    
    def __init__(self, discount_rate: float = 0.05):
        self.discount_rate = discount_rate
    
    def calculate_discount(self, price: float) -> float:
        return price * self.discount_rate
    
    def get_strategy_name(self) -> str:
        return f"Regular ({self.discount_rate*100}% discount)"

class VIPDiscountStrategy(DiscountStrategy):
    """Discount strategy for VIP customers"""
    
    def __init__(self, discount_rate: float = 0.25):
        self.discount_rate = discount_rate
    
    def calculate_discount(self, price: float) -> float:
        return price * self.discount_rate
    
    def get_strategy_name(self) -> str:
        return f"VIP ({self.discount_rate*100}% discount)"

class StudentDiscountStrategy(DiscountStrategy):
    """Discount strategy for student customers"""
    
    def __init__(self, discount_rate: float = 0.10):
        self.discount_rate = discount_rate
    
    def calculate_discount(self, price: float) -> float:
        return price * self.discount_rate
    
    def get_strategy_name(self) -> str:
        return f"Student ({self.discount_rate*100}% discount)"

class DiscountStrategyFactory:
    """Factory for creating discount strategy instances"""
    
    _strategies: Dict[CustomerType, type] = {
        CustomerType.PREMIUM: PremiumDiscountStrategy,
        CustomerType.REGULAR: RegularDiscountStrategy, 
        CustomerType.VIP: VIPDiscountStrategy,
        CustomerType.STUDENT: StudentDiscountStrategy
    }
    
    @classmethod
    def create_strategy(cls, customer_type: CustomerType) -> DiscountStrategy:
        """Create appropriate discount strategy for customer type"""
        strategy_class = cls._strategies.get(customer_type)
        
        if strategy_class is None:
            raise ValueError(f"No strategy available for customer type: {customer_type}")
        
        return strategy_class()
    
    @classmethod
    def get_available_strategies(cls) -> Dict[CustomerType, str]:
        """Get all available discount strategies"""
        return {
            customer_type: cls.create_strategy(customer_type).get_strategy_name()
            for customer_type in cls._strategies.keys()
        }

class DiscountCalculator:
    """Advanced discount calculator with strategy pattern implementation"""
    
    def __init__(self, enable_caching: bool = True):
        self.strategies: Dict[CustomerType, DiscountStrategy] = {}
        self.factory = DiscountStrategyFactory()
        self.cache: Dict[str, DiscountResult] = {} if enable_caching else None
        self.calculation_history: list = []
        
        # Pre-populate strategy cache
        self._initialize_strategies()
    
    def _initialize_strategies(self) -> None:
        """Initialize all available discount strategies"""
        for customer_type in CustomerType:
            try:
                self.strategies[customer_type] = self.factory.create_strategy(customer_type)
            except ValueError as e:
                logger.warning(f"Could not initialize strategy for {customer_type}: {e}")
    
    def _generate_cache_key(self, request: DiscountRequest) -> str:
        """Generate cache key for discount request"""
        return f"{request.customer_type.value}_{request.base_price}_{request.product_category}"
    
    def calculate_discount(self, request: DiscountRequest) -> DiscountResult:
        """Calculate discount using appropriate strategy with full logging and caching"""
        
        logger.info(f"Calculating discount for customer {request.customer_id} "
                   f"({request.customer_type.value}) on ${request.base_price} {request.product_category}")
        
        # Check cache first
        if self.cache:
            cache_key = self._generate_cache_key(request)
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                logger.info(f"Returning cached discount calculation: ${cached_result.discount_amount}")
                return cached_result
        
        # Get appropriate strategy
        try:
            strategy = self.strategies[request.customer_type]
        except KeyError:
            logger.error(f"No discount strategy available for customer type: {request.customer_type}")
            raise ValueError(f"Unsupported customer type: {request.customer_type}")
        
        # Calculate discount using strategy
        discount_amount = strategy.calculate_discount(request.base_price)
        final_price = request.base_price - discount_amount
        
        # Create result object
        result = DiscountResult(
            original_price=request.base_price,
            discount_amount=discount_amount,
            final_price=final_price,
            customer_type=request.customer_type,
            calculation_method=strategy.get_strategy_name()
        )
        
        # Cache result
        if self.cache:
            cache_key = self._generate_cache_key(request)
            self.cache[cache_key] = result
        
        # Store in calculation history
        import datetime
        self.calculation_history.append({
            'timestamp': datetime.datetime.now(),
            'customer_id': request.customer_id,
            'result': result
        })
        
        logger.info(f"Discount calculated using {strategy.get_strategy_name()}: "
                   f"${discount_amount} (Final: ${final_price})")
        
        return result
    
    def get_calculation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about discount calculations"""
        if not self.calculation_history:
            return {"total_calculations": 0}
        
        total_calcs = len(self.calculation_history)
        total_discounts = sum(calc['result'].discount_amount for calc in self.calculation_history)
        
        customer_type_counts = {}
        for calc in self.calculation_history:
            ctype = calc['result'].customer_type
            customer_type_counts[ctype.value] = customer_type_counts.get(ctype.value, 0) + 1
        
        return {
            "total_calculations": total_calcs,
            "total_discounts_given": total_discounts,
            "average_discount": total_discounts / total_calcs,
            "customer_type_breakdown": customer_type_counts,
            "cache_hit_rate": self._calculate_cache_hit_rate()
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate for performance monitoring"""
        if not self.cache or not self.calculation_history:
            return 0.0
        
        # Calculate cache hit rate for performance monitoring
        return len(self.cache) / max(len(self.calculation_history), 1)

# Convenience function that wraps the complex system
def calculate_discount(price: float, customer_type: str) -> float:
    """Simple wrapper function that hides the complex architecture"""
    
    calculator = DiscountCalculator()
    
    request = DiscountRequest(
        customer_id="unknown",
        customer_type=CustomerType(customer_type),
        base_price=price,
        product_category="general"
    )
    
    result = calculator.calculate_discount(request)
    return result.discount_amount