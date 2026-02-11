fn main() {
    println!("Hello, the_lift");
    println!("{:?}", the_lift(&[vec![], vec![], vec![5,5,5],vec![],vec![],vec![],vec![]], 5));
}

fn the_lift(queues: &[Vec<u32>], capacity: u32) -> Vec<u32> {
    let mut lift_state: LiftState = LiftState::new(queues, capacity);
    print_queues(&lift_state.up_queues, &lift_state.down_queues, lift_state.capacity, &lift_state.riders);
    let mut stops: Vec<u32> = vec![];
    stops.push(0);

    let mut previous_stops: usize = 0;
    let mut current_stops: usize = stops.len();

    while current_stops > previous_stops {
        previous_stops = current_stops;
        for floor in 0..lift_state.up_queues.len()-1{
            if let Some(stop) = lift_state.stop_at(floor) {
                if stops[stops.len()-1] != stop {
                    stops.push(stop);
                }
            }
        }
        lift_state.direction = Direction::Down;
        for floor in (1..lift_state.down_queues.len()).rev() {
            if let Some(stop) = lift_state.stop_at(floor) {
                if stops[stops.len()-1] != stop {
                    stops.push(stop);
                }
            }
        }
        lift_state.direction = Direction::Up;
        current_stops = stops.len();   
    }
    // When there are no more requests the elevator stops on floor zero.
    if stops[stops.len()-1] != 0 {
        stops.push(0);
    }

    println!("{:?}", stops);
    stops
}


#[derive(Debug)]
enum Direction {
    Up,
    Down,
}

#[derive(Debug)]
struct LiftState {
    direction: Direction,
    capacity: u32,
    floor: u32,
    riders: Vec<u32>,
    up_queues: Vec<Vec<u32>>,
    down_queues: Vec<Vec<u32>>,
}

impl LiftState {
    pub fn new(queues: &[Vec<u32>], capacity: u32) -> Self {
        let mut my_self = Self {
            direction: Direction::Up,
            capacity: capacity,
            floor: 0,
            riders: vec![],
            up_queues: vec![],
            down_queues: vec![],
        };
        my_self.init_queues(queues);
        my_self
    }

    fn init_queues(&mut self, queues: &[Vec<u32>]) -> () {
        for floor in 0..queues.len() {
            let mut up_queue: Vec<u32> = vec![];
            let mut down_queue: Vec<u32> = vec![];
            for item in queues[floor].clone()  {
                if item > (floor as u32) {
                    up_queue.push(item);
                }
                if item < (floor as u32) {
                    down_queue.push(item)
                }
            }
            self.up_queues.push(up_queue);
            self.down_queues.push(down_queue);
        }
    }

    fn stop_at(&mut self, floor: usize) -> Option<u32> {
        let unloaded_at: Option<u32> = self.unload_riders(floor);
        let mut stop_requested: bool = false;
        match self.direction {
            Direction::Up => {

            }
            Direction::Down => {

            }
        }
        if stop_requested {
            return Some(floor as u32);
        }
        return unloaded_at;
    }

    fn unload_riders(&mut self, floor: usize) -> Option<u32> {
        None
    }

}

fn print_queues(up_queues: &Vec<Vec<u32>>, down_queues: &Vec<Vec<u32>>, capacity: u32, riders: &Vec<u32>) -> String {
    let mut result = format!("\nLift capacity = {capacity}\n\n Floor    Queue");
    for (i, q) in up_queues.iter().enumerate().rev() {
        result.push_str(&format!("\n{i:>4} .... {q:?} up"));
    }    
    for (i, q) in down_queues.iter().enumerate().rev() {
        result.push_str(&format!("\n{i:>4} .... {q:?} down"));
    }
    result.push_str(&format!("\n riders: {:?}", riders));
    println!("{}", result);
    result
}
