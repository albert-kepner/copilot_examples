fn main() {
    println!("Hello, the_lift");
    println!("{:?}", the_lift(&[vec![], vec![], vec![5,5,5],vec![],vec![],vec![],vec![]], 5));
}

fn the_lift(queues: &[Vec<u32>], capacity: u32) -> Vec<u32> {
    let mut lift_state: LiftState = LiftState::new(queues, capacity);
    let mut v: Vec<u32> = vec![];
    
    println!("{:?}", v);
    v
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
        let my_self = Self {
            direction: Direction::Up,
            capacity: capacity,
            floor: 0,
            riders: vec![],
            up_queues: vec![],
            down_queues: vec![],
        };
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

}