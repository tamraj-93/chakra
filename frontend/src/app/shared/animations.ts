import { 
  trigger, 
  transition, 
  style, 
  query, 
  animate, 
  group, 
  keyframes,
  state
} from '@angular/animations';

// Page transition animations
export const fadeAnimation = trigger('fadeAnimation', [
  transition('* => *', [
    query(':enter', [
      style({ opacity: 0 })
    ], { optional: true }),
    query(':leave', [
      style({ opacity: 1 }),
      animate('0.3s', style({ opacity: 0 }))
    ], { optional: true }),
    query(':enter', [
      style({ opacity: 0 }),
      animate('0.3s', style({ opacity: 1 }))
    ], { optional: true })
  ])
]);

// Slide up animation for elements
export const slideUpAnimation = trigger('slideUpAnimation', [
  transition(':enter', [
    style({ transform: 'translateY(20px)', opacity: 0 }),
    animate('0.4s ease-out', style({ transform: 'translateY(0)', opacity: 1 }))
  ])
]);

// Slide in animation for list items
export const listAnimation = trigger('listAnimation', [
  transition('* => *', [
    query(':enter', [
      style({ transform: 'translateY(10px)', opacity: 0 }),
      stagger(100, [
        animate('0.3s ease-out', style({ transform: 'translateY(0)', opacity: 1 }))
      ])
    ], { optional: true })
  ])
]);

// Pulse animation for buttons
export const pulseAnimation = trigger('pulseAnimation', [
  state('idle', style({
    transform: 'scale(1)'
  })),
  state('pulse', style({
    transform: 'scale(1)'
  })),
  transition('idle => pulse', [
    animate('0.5s', keyframes([
      style({ transform: 'scale(1)', offset: 0 }),
      style({ transform: 'scale(1.05)', offset: 0.5 }),
      style({ transform: 'scale(1)', offset: 1.0 })
    ]))
  ])
]);

// Typing indicator animation
export const typingAnimation = trigger('typingAnimation', [
  state('active', style({
    opacity: 1
  })),
  transition('void => active', [
    style({ opacity: 0 }),
    animate('0.3s ease-in', style({ opacity: 1 }))
  ]),
  transition('active => void', [
    animate('0.3s ease-out', style({ opacity: 0 }))
  ])
]);

// Chat message animation
export const chatMessageAnimation = trigger('chatMessageAnimation', [
  transition(':enter', [
    style({ opacity: 0, transform: 'translateY(10px)' }),
    animate('0.3s ease-out', style({ opacity: 1, transform: 'translateY(0)' }))
  ])
]);

// Stagger animation for multiple elements
function stagger(ms: number, animations: any[]) {
  return query(':enter', [
    style({ opacity: 0, transform: 'translateY(10px)' }),
    staggerAnimations(ms, animations)
  ], { optional: true });
}

function staggerAnimations(ms: number, animations: any[]): any {
  if (animations.length > 0) {
    return group(
      animations.map((animation, i) => {
        const delay = i * ms;
        return group([
          ...animations,
          query(':enter', style({ opacity: 0 }), { optional: true }),
          query(':enter', 
            animate(`300ms ${delay}ms ease-out`, style({ opacity: 1, transform: 'translateY(0)' })),
            { optional: true }
          )
        ]);
      })
    );
  }
  return [];
}