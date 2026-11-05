package com.campus.headlines.aspect;

import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.springframework.stereotype.Component;

/**
 * 控制器统一日志切面：演示 Spring AOP 的 @Aspect / @Pointcut / @Around。
 */
@Slf4j
@Aspect
@Component
public class LogAspect {

    @Pointcut("execution(public * com.campus.headlines.controller..*.*(..))")
    public void controllerPointcut() {
    }

    @Around("controllerPointcut()")
    public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        String target = joinPoint.getTarget().getClass().getSimpleName()
                + "." + joinPoint.getSignature().getName();
        try {
            Object result = joinPoint.proceed();
            log.info("[AOP] {} 执行成功，耗时 {} ms", target, System.currentTimeMillis() - start);
            return result;
        } catch (Throwable throwable) {
            log.warn("[AOP] {} 执行异常：{}，耗时 {} ms",
                    target, throwable.getMessage(), System.currentTimeMillis() - start);
            throw throwable;
        }
    }
}
